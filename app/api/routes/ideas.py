from fastapi import APIRouter,status,Depends, Query
from fastapi import UploadFile, File, Form
from typing import List, Annotated

from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.ideas import IdeaRepository
from app.auth.permissions import Permissions, has_permission
from app.api.deps import CurrentUser
from app.schema import pagination
from app.schema.idea import IdeaListResponse, IdeasListRequest, IdeaResponse


router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
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


@router.get("/", response_model=IdeaListResponse)
# @has_permission(Permissions.READ_IDEA)
async def get_all_ideas(query_params: Annotated[IdeasListRequest, Query()], current_user: CurrentUser, db: Session = Depends(get_db)):
    user_id = current_user.id
    # check if user is admin
    if current_user.role.name in ["ADMIN", "QA MANAGER"]:
        show_anoymous_users = True
    else:
        show_anoymous_users = False

    idea_repo = IdeaRepository(db)
    ideas, pagination = await idea_repo.get_all_ideas(user_id=user_id, filter_params=query_params)
    data = []
    for idea in ideas:
        idea_response = IdeaResponse(
            id = idea.id,
            title = idea.title,
            description = idea.description,
            thumbnail = idea.thumbnail,
            posted_by = idea.user.username if idea.user.username or show_anoymous_users else "Anonymous",
            posted_on = idea.created_at,
        )
        data.append(idea_response)
    
    idea_list_response = IdeaListResponse(
        data = data,
        pagination = pagination
    )
    return idea_list_response