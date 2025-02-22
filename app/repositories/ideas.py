from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import UploadFile
import shutil
from pathlib import Path
import io,os
from app.models.idea_model import Idea
from app.models.file_model import File
from app.models.comment_model import Comment
from app.models.like_model import Like


class IdeaRepository:

    def __init__(self,db: Session):
        
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
                    colideaid=new_idea.colideaid,
                    colfilename=file.filename,
                    colfilelocation=file_location,  # Store the actual file path
                    colfiletype=file.content_type
                )
                self.db.add(new_file)

        self.db.commit()
        self.db.refresh(new_idea)
        return new_idea