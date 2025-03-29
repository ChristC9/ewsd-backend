from calendar import c
import select
from typing import List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select, func, delete
from fastapi import UploadFile
import shutil
from pathlib import Path
import io,os
from app.models.idea_model import Idea
from app.models.file_model import File
from app.models.comment_model import Comment
from app.models.department_model import Department
from app.models.user_model import User
from app.models.like_model import Like
from app.models.report_model import Report
from app.schema import idea as idea_schema
from app.schema.idea import IdeasListRequest
from app.utils.helpers import compute_pagination
from fastapi import HTTPException,status


class IdeaRepository:
    IDEA_NOT_FOUND_MSG = "Idea not found"

    def __init__(self, db: AsyncSession):
        
        self.db = db
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(parents=True,exist_ok=True)
    
    async def convert_file_to_bytes(self, file: UploadFile) -> bytes:
        file_content = await file.read()
        file_bytes_io = io.BytesIO(file_content)
        return file_bytes_io.getvalue()
    

    async def _save_file(self, file: UploadFile) -> str:
    
        file_path = self.upload_dir / file.filename
        
        counter = 1
        while file_path.exists():
            name, ext = os.path.splitext(file.filename)
            file_path = self.upload_dir / f"{name}_{counter}{ext}"
            counter += 1

        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        finally:
            file.file.close()
        
        return str(file_path)


    async def create_idea(self, 
                   title: str,
                   description: str,
                   posted_by: int,
                   category_id: int,
                   thumbnail: UploadFile = None,
                   is_posted_anon: bool = False,
                   files: List[UploadFile] = None) -> Idea:
        

        if thumbnail:
            thumbnail_bytes = await self.convert_file_to_bytes(thumbnail)

        new_idea = Idea (
            title = title,
            description = description,
            thumbnail = thumbnail_bytes,
            categoryid = int(category_id),
            postedby = int(posted_by),
            postedon = date.today(),
            ispostedanon = is_posted_anon,
            isactived = True
        )
        print(f"New Idea for user id is : {new_idea.postedby}")
        self.db.add(new_idea)
        await self.db.flush()

        if files:
            for file in files:
                file_location = await self._save_file(file)
                
                new_file = File(
                    ideaid=new_idea.id,
                    filename=file.filename,
                    filelocation=file_location,  # Store the actual file path
                    filetype=file.content_type
                )
                self.db.add(new_file)

        await self.db.commit()
        await self.db.refresh(new_idea)
        return new_idea
    

    def _build_count_subqueries(self):
        likes_count = (
            select(Like.ideaid, func.count(Like.id).label('likes_count'))
            .where(Like.isliked == True)
            .group_by(Like.ideaid)
            .subquery()
        )
        
        dislikes_count = (
            select(Like.ideaid, func.count(Like.id).label('dislikes_count'))
            .where(Like.isliked == False)
            .group_by(Like.ideaid)
            .subquery()
        )
        
        comments_count = (
            select(Comment.ideaid, func.count(Comment.id).label('comments_count'))
            .group_by(Comment.ideaid)
            .subquery()
        )
        
        return likes_count, dislikes_count, comments_count

    def _build_base_query(self, likes_count, dislikes_count, comments_count):
        popularity_score = func.coalesce(likes_count.c.likes_count, 0) - func.coalesce(dislikes_count.c.dislikes_count, 0)
        
        return (
            select(
                Idea,
                func.coalesce(likes_count.c.likes_count, 0).label('likes_count'),
                func.coalesce(dislikes_count.c.dislikes_count, 0).label('dislikes_count'),
                func.coalesce(comments_count.c.comments_count, 0).label('comments_count'),
                Department,
                popularity_score.label('popularity_score')
            )
            .outerjoin(likes_count, Idea.id == likes_count.c.ideaid)
            .outerjoin(dislikes_count, Idea.id == dislikes_count.c.ideaid)
            .outerjoin(comments_count, Idea.id == comments_count.c.ideaid)
            .join(User, Idea.postedby == User.id)
            .join(Department, User.department_id == Department.id)
            .where(Idea.isactived == True)
            .where(User.isdisabled == False)
        )

    def _apply_filters(self, query, user_id: int, filter_params: IdeasListRequest):
        if filter_params.filter_category:
            query = query.where(Idea.categoryid.in_(filter_params.filter_category))
        if filter_params.search:
            query = query.where(or_(
                Idea.title.ilike(f"%{filter_params.search}%"),
                Idea.description.ilike(f"%{filter_params.search}%")
            ))
        if filter_params.filter_my:
            query = query.where(Idea.postedby == user_id)
        if filter_params.filter_department:
            query = query.where(Department.id.in_(filter_params.filter_department))
        if filter_params.filter_reported:
            query = query.where(Idea.isreported == True)
        return query

    async def get_all_ideas(self, user_id: int, filter_params: IdeasListRequest):
        likes_count, dislikes_count, comments_count = self._build_count_subqueries()
        query = self._build_base_query(likes_count, dislikes_count, comments_count)
        query = self._apply_filters(query, user_id, filter_params)

        # Apply sorting
        sort_params = [
            (likes_count.c.likes_count, filter_params.sort_by_likes),
            (Idea.created_at, filter_params.sort_by_date),
            (func.coalesce(likes_count.c.likes_count, 0) - func.coalesce(dislikes_count.c.dislikes_count, 0), filter_params.sort_by_popularity),
            (Idea.views_count, filter_params.sort_by_most_viewed),
        ]

        for field, order in sort_params:
            if order is not None:
                query = query.order_by(field.desc() if order == -1 or order == True else field.asc())

        # Apply pagination
        offset = (filter_params.page - 1) * filter_params.limit
        query = query.offset(offset).limit(filter_params.limit)

        # Execute query and format results
        result = await self.db.execute(query)
        rows = result.unique().all()
        ideas_with_counts = [{
            "idea": row[0],
            "likes_count": row[1],
            "dislikes_count": row[2],
            "comments_count": row[3],
            "department": row[4],
            "reports_count": len(row[0].reports)
        } for row in rows]

        # Get total count
        total_query = select(func.count(Idea.id)).join(User, Idea.postedby == User.id).join(Department, User.department_id == Department.id)
        total_query = self._apply_filters(total_query, user_id, filter_params)
        total = await self.db.execute(total_query)
        total = total.scalar_one()

        pagination = compute_pagination(total, filter_params.page, filter_params.limit)
        return ideas_with_counts, pagination


    async def get_all_ideas_ids(self):
        query = (
            select(Idea.id)
            .where(Idea.isactived == True)
        )

        result = await self.db.execute(query)
        ideas_ids = result.scalars().all()
        return ideas_ids
    

    async def get_idea_by_id(self, idea_id: int)-> Idea:
    
        likes_count = (
            select(Like.ideaid, func.count(Like.id).label('likes_count'))
            .where(Like.isliked == True)
            .group_by(Like.ideaid)
            .subquery()
        )

        # Subquery to count dislikes for each idea
        dislikes_count = (
            select(Like.ideaid, func.count(Like.id).label('dislikes_count'))
            .where(Like.isliked == False)
            .group_by(Like.ideaid)
            .subquery()
        )

        # Subquery to count comments for each idea
        comments_count = (
            select(Comment.ideaid, func.count(Comment.id).label('comments_count'))
            .group_by(Comment.ideaid)
            .subquery()
        )

        query = (
            select(
            Idea,
            func.coalesce(likes_count.c.likes_count, 0).label('likes_count'),
            func.coalesce(dislikes_count.c.dislikes_count, 0).label('dislikes_count'),
            func.coalesce(comments_count.c.comments_count, 0).label('comments_count'),
            Department
            )
            .outerjoin(likes_count, Idea.id == likes_count.c.ideaid)
            .outerjoin(dislikes_count, Idea.id == dislikes_count.c.ideaid)
            .outerjoin(comments_count, Idea.id == comments_count.c.ideaid)
            .join(User, Idea.postedby == User.id)
            .join(Department, User.department_id == Department.id)
            .where(Idea.isactived == True)
            .where(User.isdisabled == False)  # Only return ideas from users who are not disabled
            .where(Idea.id == idea_id)
        )

        result = await self.db.execute(query)
        row = result.unique().first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self.IDEA_NOT_FOUND_MSG)

        idea_details = {
            "idea": row[0],
            "likes_count": row[1],
            "dislikes_count": row[2], 
            "comments_count": row[3],
            "department": row[4],
            "reports_count": len(row[0].reports),
            # "comments": comments
        }

        return idea_details


    async def update_idea(self, 
                    idea_id: int, 
                    title: str,
                    description: str,
                    category_id: int,
                    thumbnail: UploadFile = None,
                    is_posted_anon: bool = False,
                    files: List[UploadFile] = None) -> Idea:
    
        # First, verify the idea exists
        result = await self.db.execute(select(Idea).where(Idea.id == idea_id))
        idea = result.scalar_one_or_none()
        
        if not idea:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Idea with ID {idea_id} not found")
        
        # Check if category exists
        category = await self.db.execute(select(Department).where(Department.id == category_id))
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with ID {category_id} not found")
        
        # Update basic fields
        idea.title = title
        idea.description = description
        idea.categoryid = category_id
        idea.ispostedanon = is_posted_anon
        
        # Handle thumbnail update
        if thumbnail:
            try:
                thumbnail_bytes = await self.convert_file_to_bytes(thumbnail)
                idea.thumbnail = thumbnail_bytes
            except Exception as e:
                print(f"Error processing thumbnail: {str(e)}")
                # Don't update the thumbnail if there's an error
        
        # Add new files if provided
        if files:
            for file in files:
                try:
                    file_location = await self._save_file(file)
                    
                    new_file = File(
                        ideaid=idea_id,
                        filename=file.filename,
                        filelocation=file_location,
                        filetype=file.content_type
                    )
                    self.db.add(new_file)
                except Exception as e:
                    print(f"Error processing file {file.filename}: {str(e)}")
                    # Continue with other files
        
        # Save changes
        await self.db.commit()
        await self.db.refresh(idea)
        
        return idea
    
    async def delete_idea(self, idea_id: int) -> Idea:
    
        idea = await self.db.execute(select(Idea).where(Idea.id == idea_id))
        if not idea:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self.IDEA_NOT_FOUND_MSG)
        await self.db.delete(idea)
        await self.db.commit()
        return {"message": f"Idea id {idea_id} is deleted successfully"}


    
    async def get_idea_reports(self, idea_id: int):
        query = (
            select(Report)
            .where(Report.ideaid == idea_id)
        )

        result = await self.db.execute(query)
        reports = result.unique().scalars() 
        return reports


    async def report_idea(self, report_create: idea_schema.IdeaReportCreate):

        idea = await self.get_idea_by_id(report_create.idea_id)
        if not idea:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
        report = Report(
            reportedby = report_create.user_id,
            ideaid = report_create.idea_id,
            reportedreason = report_create.reason
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report


    async def get_report_by_id(self, report_id: int):
        query = (
            select(Report)
            .where(Report.id == report_id)
        )

        result = await self.db.execute(query)
        report = result.unique().first()
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        return report


    async def delete_report_idea(self, report_id: int):
        query = delete(Report).where(Report.id == report_id)
        await self.db.execute(query)
        await self.db.commit()
        return f"Report id {report_id} is deleted successfully"
        

    async def update_idea_views_count(self, idea_id: int):
        query = (
            select(Idea)
            .where(Idea.id == idea_id)
        )
        result = await self.db.execute(query)
        idea = result.unique().scalar_one_or_none()
        
        if not idea:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self.IDEA_NOT_FOUND_MSG)
        
        idea.views_count = idea.views_count + 1
        await self.db.commit()
        await self.db.refresh(idea)
        return idea

        
    async def get_raw_idea_by_id(self, idea_id: int):
        query = (
            select(Idea)
            .where(Idea.id == idea_id)
        )
        result = await self.db.execute(query)
        idea = result.unique().scalar_one_or_none()
        
        return idea
       

