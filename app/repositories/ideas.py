from calendar import c
import select
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select, func
from fastapi import UploadFile
import shutil
from pathlib import Path
import io,os
from app.api.routes import departments
from app.models.idea_model import Idea
from app.models.file_model import File
from app.models.comment_model import Comment
from app.models.department_model import Department
from app.models.user_model import User
from app.models.like_model import Like

from app.schema import pagination
from app.schema import idea
from app.schema.idea import IdeasListRequest

from app.utils.helpers import compute_pagination
from fastapi import HTTPException,status


class IdeaRepository:

    def __init__(self, db: AsyncSession):
        
        self.db = db
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(parents=True,exist_ok=True)
    
    async def convert_file_to_bytes(self, file: UploadFile) -> bytes:
        file_bytes = io.BytesIO(file.file.read())
        return file_bytes
    

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
        
        thumbnail_bytes = None

        # if thumbnail:
        #     thumbnail_bytes = await self.convert_file_to_bytes(thumbnail)

        new_idea = Idea (
            title = title,
            description = description,
            thumbnail = None,
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
    

    async def get_all_ideas(self, user_id: int, filter_params: IdeasListRequest):
        # Subquery to count likes for each idea
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
        )

        filters = [
            (Idea.categoryid.in_(filter_params.filter_category)) if filter_params.filter_category else None,
            (or_(
                Idea.title.ilike(f"%{filter_params.search}%"), 
                Idea.description.ilike(f"%{filter_params.search}%")
            )) if filter_params.search else None,
            (Idea.postedby == user_id) if filter_params.filter_my else None,
            (Department.id.in_(filter_params.filter_department)) if filter_params.filter_department else None
        ]

        for condition in filters:
            if condition is not None:
                query = query.where(condition)

        sort_params = [
            (likes_count.c.likes_count, filter_params.sort_by_likes),
            (Idea.created_at, filter_params.sort_by_date),
        ]

        for field, order in sort_params:
            if order is not None:
                query = query.order_by(field.desc() if order == -1 or order == True else field.asc())

        offset = (filter_params.page - 1) * filter_params.limit
        query = query.offset(offset).limit(filter_params.limit)

        result = await self.db.execute(query)
        rows = result.unique().all()
        ideas_with_counts = [
            {
            "idea": row[0],
            "likes_count": row[1],
            "dislikes_count": row[2], 
            "comments_count": row[3],
            "department": row[4]
            } for row in rows
        ]

        total_query = (
            select(func.count(Idea.id))
            .join(User, Idea.postedby == User.id)
            .join(Department, User.department_id == Department.id)
            .where(Idea.isactived == True)
        )
        for condition in filters:  
            if condition is not None:
                total_query = total_query.where(condition)
        
        total_result = await self.db.execute(total_query)
        total = total_result.scalar_one()
        pagination = compute_pagination(total, filter_params.page, filter_params.limit)
        return ideas_with_counts, pagination


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
            .where(Idea.id == idea_id)
        )

        result = await self.db.execute(query)
        row = result.unique().first()
        idea_details = {
            "idea": row[0],
            "likes_count": row[1],
            "dislikes_count": row[2], 
            "comments_count": row[3],
            "department": row[4],
        }
        if not idea_details:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")

        return idea_details




        

        
       

