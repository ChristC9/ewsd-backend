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
from app.models.idea_model import Idea
from app.models.file_model import File
from app.models.comment_model import Comment
from app.models.like_model import Like

from app.schema import pagination
from app.schema.idea import IdeasListRequest

from app.utils.helpers import compute_pagination


class IdeaRepository:

    def __init__(self,db: AsyncSession):
        
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
                   thumbnail: UploadFile = None,
                   is_posted_anon: bool = False,
                   files: List[UploadFile] = None) -> Idea:
        
        thumbnail_bytes = None

        if thumbnail:
            thumbnail_bytes = await self.convert_file_to_bytes(thumbnail)

        new_idea = Idea (
            title = title,
            description = description,
            thumbnail = thumbnail_bytes,
            postedby = posted_by,
            postedon = date.today(),
            ispostedanon = is_posted_anon,
            isactived = True
        )
        self.db.add(new_idea)
        self.db.flush()

        if files:
            for file in files:
                file_location = await self._save_file(file)
                
                new_file = File(
                    colideaid=new_idea.id,
                    colfilename=file.filename,
                    colfilelocation=file_location,  # Store the actual file path
                    colfiletype=file.content_type
                )
                self.db.add(new_file)

        self.db.commit()
        self.db.refresh(new_idea)
        return new_idea
    

    async def get_all_ideas(self, user_id: int, filter_params: IdeasListRequest):
        query = (
           select(Idea).where(Idea.isactived == True)
        )
        filters = [
            (Idea.categoryid.in_(filter_params.filter_category)) if filter_params.filter_category else None,
            (or_(
                Idea.title.ilike(f"%{filter_params.search}%"), 
                Idea.description.ilike(f"%{filter_params.search}%")
                )
            ) if filter_params.search else None,
            (Idea.postedby == user_id) if filter_params.filter_my else None
        ]

        for condition in filters:
            if condition is not None:
                query = query.where(condition)
        
        sort_params = [
            (Idea.created_at, filter_params.sort_date),
        ]

        for field, order in sort_params:
            if order:
                query = query.order_by(field.desc() if order == -1 else field.asc())

        offset = (filter_params.page - 1) * filter_params.limit
        query = query.offset(offset).limit(filter_params.limit)

        result = await self.db.execute(query)
        ideas = result.unique().scalars().all()

        total_query = select(func.count(Idea.id)).where(Idea.isactived == True)    
        for condition in filters:  
            if condition is not None:
                total_query = total_query.where(condition)
        
        total_result = await self.db.execute(total_query)
        total = total_result.scalar_one()
        pagination = compute_pagination(total, filter_params.page, filter_params.limit)
        return ideas, pagination






        

        
       

