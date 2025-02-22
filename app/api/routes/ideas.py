from fastapi import APIRouter,status,Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.ideas import IdeaRepository
from app.auth.permissions import Permissions, has_permission
from fastapi import UploadFile, File, Form
from typing import List

router = APIRouter()

@router.post("/ideas/", status_code=status.HTTP_201_CREATED)
@has_permission(Permissions.CREATE_IDEA)
async def create_idea(
    title: str = Form(...),
    description: str = Form(None),
    posted_by: int = Form(...),
    thumbnail: UploadFile = File(None),
    files: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    
    idea_repo = IdeaRepository(db)
    return await idea_repo.create_idea(title, description, posted_by, thumbnail, files)