from fastapi import APIRouter,status,Depends, Query
from fastapi import UploadFile, File, Form
from typing import List, Annotated

from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.ideas import IdeaRepository
from app.auth.permissions import Permissions, has_permission
from app.api.deps import CurrentUser
from app.schema.idea import IdeaListResponse, IdeasListRequest, IdeaResponse
from app.schema.category import CategoryBase
from app.schema.schema import DepartmentBase


router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
@has_permission(Permissions.CREATE_IDEA)
async def create_idea(
    current_user: CurrentUser,
    title: str = Form(...),
    description: str = Form(None),
    posted_by: int = Form(...),
    category_id: int = Form(...),
    thumbnail: UploadFile = File(None),
    is_posted_anon: bool = Form(False),
    files: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    
    idea_repo = IdeaRepository(db)
    return await idea_repo.create_idea(title, description, posted_by, category_id, thumbnail, is_posted_anon, files)


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
    for item in ideas:
        idea_response = IdeaResponse(
            id = item["idea"].id,
            title = item["idea"].title,
            description = item["idea"].description,
            likes_count = item["likes_count"],
            dislikes_count = item["dislikes_count"],
            comments_count = item["comments_count"],
            thumbnail = item["idea"].thumbnail,
            posted_by = {
                "id": item["idea"].user.id,
                "firstname": item["idea"].user.firstname,
                "lastname": item["idea"].user.lastname,
            } if not item["idea"].ispostedanon or show_anoymous_users else {
                "id": None,
                "firstname": "Anonymous",
                "lastname": "User",
            },
            posted_on = item["idea"].created_at,
            department = DepartmentBase(
                id = item["department"].id,
                name = item["department"].name,
                created_by= item["department"].created_by,
                created_at= item["department"].created_at,
                updated_at= item["department"].updated_at,
            ),
            category = CategoryBase(
                id = item["idea"].category.categoryid,
                name = item["idea"].category.categoryname,
                created_by= item["idea"].category.created_by,
                created_at= item["idea"].category.created_at,
            )
        )
        data.append(idea_response)
    
    idea_list_response = IdeaListResponse(
        data = data,
        pagination = pagination
    )
    return idea_list_response