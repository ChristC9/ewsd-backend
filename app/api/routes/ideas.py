import re
from fastapi import APIRouter, HTTPException,status,Depends, Query
from fastapi import UploadFile, File, Form
from typing import List, Annotated
from fastapi.responses import StreamingResponse


from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.report_model import Report
from app.repositories.ideas import IdeaRepository
from app.auth.permissions import Permissions, has_permission
from app.api.deps import CurrentUser
from ..deps import get_current_user
from app.schema import idea
from app.schema.idea import IdeaListResponse, IdeasListRequest, IdeaResponse, FileResponse, IdeaReportCreate, ReportRequest
from app.schema.category import CategoryBase
from app.schema.schema import DepartmentBase
from app.models.user_model import User
from sqlalchemy import select

import csv
from io import StringIO


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
    
    user = await db.execute(select(User).where(User.id == posted_by))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {posted_by} not found")
    
    if user.isdisabled:
        raise HTTPException(status_code=400, detail=f"User account {posted_by} is disabled and cannot post ideas")
    
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
            reports_count = item["reports_count"],
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

@router.get('/{idea_id}', response_model=IdeaResponse)
# @has_permission(Permissions.READ_IDEA)
async def get_idea_by_id(idea_id: int, current_user: CurrentUser, db: Session = Depends(get_db)):
    # check if user is admin
    if current_user.role.name in ["ADMIN", "QA MANAGER"]:
        show_anoymous_users = True
    else:
        show_anoymous_users = False
    idea_repo = IdeaRepository(db)
    item = await idea_repo.get_idea_by_id(idea_id)
    idea_response = IdeaResponse(
            id = item["idea"].id,
            title = item["idea"].title,
            description = item["idea"].description,
            likes_count = item["likes_count"],
            dislikes_count = item["dislikes_count"],
            comments_count = item["comments_count"],
            reports_count = item["reports_count"],  
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
            ),
            files=[FileResponse(
                id = file.id,
                filename = file.filename,
                filetype = file.filetype
            ) for file in item["idea"].files]
            if item["idea"].files else []   
        )
    return idea_response


@router.put('/{idea_id}', response_model=IdeaResponse)
# @has_permission(Permissions.UPDATE_IDEA)
async def update_idea(idea_id: int, idea_data: IdeasListRequest, current_user: CurrentUser, db: Session = Depends(get_db)):
    idea_repo = IdeaRepository(db)
    return await idea_repo.update_idea(idea_id, idea_data)


@router.delete('/{idea_id}', status_code=status.HTTP_204_NO_CONTENT)
# @has_permission(Permissions.DELETE_IDEA)
async def delete_idea(idea_id: int, current_user: CurrentUser, db: Session = Depends(get_db)):
    idea_repo = IdeaRepository(db)
    return await idea_repo.delete_idea(idea_id)


@router.get("/export/csv", status_code=status.HTTP_200_OK)
@has_permission(Permissions.READ_IDEA)
async def export_ideas_csv(
    query_params: Annotated[IdeasListRequest, Query()], 
    current_user: CurrentUser, 
    db: Session = Depends(get_db)
):
    # Generate CSV data from ideas
    idea_repo = IdeaRepository(db)
    ideas, _ = await idea_repo.get_all_ideas(user_id=current_user.id, filter_params=query_params)

    # Create a StringIO buffer to hold CSV data
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)

    # Write header row
    csv_writer.writerow(['Title', 'Author', 'Category', 'Department', 'Likes', 'Dislikes', 'Comments', 'Reports', 'Posted On'])

    # Check if user can see anonymous posts
    show_anonymous_users = current_user.role.name in ["ADMIN", "QA MANAGER"]

    # Write data rows
    for item in ideas:
        csv_writer.writerow([
            item["idea"].title,
            f"{item['idea'].user.firstname} {item['idea'].user.lastname}" if not item["idea"].ispostedanon or show_anonymous_users else "Anonymous User",
            item["idea"].category.categoryname,
            item["department"].name,
            item["likes_count"],
            item["dislikes_count"],
            item["comments_count"],
            item["reports_count"],
            item["idea"].created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    # Set the position to the start of the buffer
    csv_buffer.seek(0)

    # Return a StreamingResponse
    return StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment;filename=ideas_export.csv"}
    )
    

@router.get("/{idea_id}/reports", status_code=status.HTTP_200_OK)
async def get_all_idea_reports(idea_id: int, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    idea_repo = IdeaRepository(db)
    reports = await idea_repo.get_idea_reports(idea_id)
    reportsResponse = [report.to_dict() for report in reports]
    return reportsResponse
    

@router.post("/{idea_id}/reports")
async def report_idea(
    idea_id: int, 
    reportRequest: ReportRequest, 
    current_user: CurrentUser, 
    db: AsyncSession = Depends(get_db)
):
    idea_repo = IdeaRepository(db)
    # Set the user_id and idea_id from the path and current user
    report_data = IdeaReportCreate(
        user_id = current_user.id,
        idea_id = idea_id,
        reason = reportRequest.reason
    )
    await idea_repo.report_idea(report_data)
    return {"detail": "Idea reported successfully"}


@router.delete("/{idea_id}/reports/{report_id}")
async def delete_idea_report(idea_id: int, report_id: int, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    idea_repo = IdeaRepository(db)
    message = await idea_repo.delete_report_idea(report_id)
    return {"detail": message}
    

