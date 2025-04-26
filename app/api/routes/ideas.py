from fastapi import APIRouter, HTTPException,status,Depends, Query, BackgroundTasks
from fastapi import UploadFile, File, Form
from typing import List, Annotated, Optional
from fastapi.responses import StreamingResponse
import base64

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.ideas import IdeaRepository
from app.repositories.users import UserRepository
from app.auth.permissions import Permissions, has_permission
from app.api.deps import CurrentUser
from app.schema.comment import CommentResponse
from app.schema.idea import IdeaListResponse, IdeasListRequest, IdeaResponse, FileResponse, IdeaReportCreate, ReportRequest
from app.schema.category import CategoryBase
from app.schema.schema import DepartmentBase
from app.models.user_model import User
from app.models.comment_model import Comment
from app.utils.helpers import send_idea_submitted_email
from sqlalchemy import select
from typing import Annotated, Optional
import csv
from io import StringIO, BytesIO
import zipfile
from pathlib import Path


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
    username = f"{current_user.firstname} {current_user.lastname}"

    user = await db.execute(select(User).where(User.id == posted_by))
    user = user.unique().scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {posted_by} not found")
    
    if user.isdisabled:
        raise HTTPException(status_code=400, detail=f"User account {posted_by} is disabled and cannot post ideas")
    
    idea_repo = IdeaRepository(db)
    new_idea = await idea_repo.create_idea(title, description, posted_by, category_id, thumbnail, is_posted_anon, files)
    
    # Create response dictionary
    response_data = {
        "id": new_idea.id,
        "title": new_idea.title,
        "description": new_idea.description,
        "category_id": new_idea.categoryid,
        "posted_by": new_idea.postedby,
        "posted_on": new_idea.postedon,
        "is_posted_anon": new_idea.ispostedanon,
        "files": [
            new_idea.files[i].filename if new_idea.files else None for i in range(len(new_idea.files))
        ],
        "message": "Idea created successfully"
    }
    
    # Add thumbnail as Base64 if it exists
    if new_idea.thumbnail:
        # Convert binary to Base64 string
        thumbnail_base64 = base64.b64encode(new_idea.thumbnail).decode('utf-8')
        response_data["thumbnail"] = thumbnail_base64
    else:
        response_data["thumbnail"] = None
    
    user_repo = UserRepository(db)
    new_idea_title = new_idea.title
    qa_mails = await user_repo.get_mails_by_role("QACOORDINATOR", current_user.department_id)
    send_idea_submitted_email(qa_mails, new_idea_title, username)
    return response_data


@router.get("/", response_model=IdeaListResponse)
# @has_permission(Permissions.READ_IDEA)
async def get_all_ideas(query_params: Annotated[IdeasListRequest, Query()], current_user: CurrentUser, db: Session = Depends(get_db)):
    user_id = current_user.id
    # check if user is admin
    if current_user.role.name in ["ADMIN", "QA_MANAGER"]:
        show_anoymous_users = True
    else:
        show_anoymous_users = False

    idea_repo = IdeaRepository(db)
    ideas, pagination = await idea_repo.get_all_ideas(user_id=user_id, filter_params=query_params)
    data = []
    for item in ideas:

        thumbnail_b64 = None
        if item["idea"].thumbnail:
            thumbnail_b64 = base64.b64encode(item["idea"].thumbnail).decode('utf-8')
        
        idea_response = IdeaResponse(
            id = item["idea"].id,
            title = item["idea"].title,
            description = item["idea"].description,
            likes_count = item["likes_count"],
            dislikes_count = item["dislikes_count"],
            comments_count = item["comments_count"],
            views_count= item["idea"].views_count,
            reports_count = item["reports_count"],
            thumbnail =  thumbnail_b64,
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
            if item["idea"].files else [],
            current_user_reaction = item.get("current_user_reaction", None)
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
    if current_user.role.name in ["ADMIN", "QA_MANAGER"]:
        show_anoymous_users = True
    else:
        show_anoymous_users = False
    
    idea_repo = IdeaRepository(db)
    item = await idea_repo.get_idea_by_id(idea_id,current_user.id)
    
    # Convert thumbnail to base64 if it exists
    thumbnail_b64 = None
    if item["idea"].thumbnail:
        thumbnail_b64 = base64.b64encode(item["idea"].thumbnail).decode('utf-8')
    
    # Get comments for this idea
    comments_query = (
        select(Comment)
        .where(Comment.ideaid == idea_id)
        .order_by(Comment.postedon.desc())  # Most recent comments first
    )
    comments_result = await db.execute(comments_query)
    comments = comments_result.scalars().all()
    
    # Format comments for the response
    comments_response = []
    for comment in comments:
        # Get the user who posted the comment
        user_query = select(User).where(User.id == comment.postedby)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        # Determine username based on anonymity settings
        username = None
        if user and (not comment.ispostedanon or show_anoymous_users):
            username = f"{user.firstname} {user.lastname}"
        elif comment.ispostedanon:
            username = "Anonymous User"
            
        # Create CommentResponse object, matching your schema
        comment_response = CommentResponse(
            id=comment.id,
            commentuid=comment.commentuid,
            comment=comment.comment,
            ideaid=comment.ideaid,
            postedby=comment.postedby,
            postedon=comment.postedon,
            ispostedanon=comment.ispostedanon,
            username=username
        )
        comments_response.append(comment_response)
    
    idea_response = IdeaResponse(
            id = item["idea"].id,
            title = item["idea"].title,
            description = item["idea"].description,
            likes_count = item["likes_count"],
            dislikes_count = item["dislikes_count"],
            comments_count = item["comments_count"],
            views_count = item["idea"].views_count,
            reports_count = item["reports_count"],  
            thumbnail = thumbnail_b64,
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
            if item["idea"].files else [],
            comments = comments_response,
            current_user_reaction = item.get("current_user_reaction", None)
        )
    
    # Update the views count
    await idea_repo.update_idea_views_count(idea_id)
    return idea_response


@router.put('/{idea_id}', response_model=IdeaResponse)
# @has_permission(Permissions.UPDATE_IDEA)
async def update_idea(
    idea_id: int,
    current_user: CurrentUser,
    title: str = Form(...),
    description: str = Form(None),
    category_id: int = Form(...),

    thumbnail: Optional[UploadFile] = File(None),  # Ensure it's marked as Optional
    is_posted_anon: bool = Form(False),
    files: List[UploadFile] = File(None),
    update_thumbnail: bool = Form(False),  # Add a flag to indicate if thumbnail should be updated
    db: Session = Depends(get_db)
):
    # Check if the user has permission to update this idea
    # You might want to add permission checks here

    idea_repo = IdeaRepository(db)

    # Update the idea
    await idea_repo.update_idea(
        idea_id=idea_id,
        title=title,
        description=description,
        category_id=category_id,
        thumbnail=thumbnail,
        is_posted_anon=is_posted_anon,
        files=files,
        update_thumbnail=update_thumbnail  # Pass the flag
    )

    # Rest of the code remains the same
    # Get the updated idea details
    idea_details = await idea_repo.get_idea_by_id(idea_id)

    # Format the response
    # Convert thumbnail to base64 if it exists
    thumbnail_b64 = None
    if idea_details["idea"].thumbnail:
        thumbnail_b64 = base64.b64encode(idea_details["idea"].thumbnail).decode('utf-8')

    # Check if user is admin
    show_anonymous_users = current_user.role.name in ["ADMIN", "QA MANAGER"]

    # Build the response object
    idea_response = IdeaResponse(
        id=idea_details["idea"].id,
        title=idea_details["idea"].title,
        description=idea_details["idea"].description,
        likes_count=idea_details["likes_count"],
        dislikes_count=idea_details["dislikes_count"],
        comments_count=idea_details["comments_count"],
        views_count=idea_details["idea"].views_count,
        reports_count=idea_details["reports_count"],  
        thumbnail=thumbnail_b64,
        posted_by={
            "id": idea_details["idea"].user.id,
            "firstname": idea_details["idea"].user.firstname,
            "lastname": idea_details["idea"].user.lastname,
        } if not idea_details["idea"].ispostedanon or show_anonymous_users else {
            "id": None,
            "firstname": "Anonymous",
            "lastname": "User",
        },
        posted_on=idea_details["idea"].created_at,
        department=DepartmentBase(
            id=idea_details["department"].id,
            name=idea_details["department"].name,
            created_by=idea_details["department"].created_by,
            created_at=idea_details["department"].created_at,
            updated_at=idea_details["department"].updated_at,
        ),
        category=CategoryBase(
            id=idea_details["idea"].category.categoryid,
            name=idea_details["idea"].category.categoryname,
            created_by=idea_details["idea"].category.created_by,
            created_at=idea_details["idea"].category.created_at,
        )
    )

    return idea_response


@router.delete('/{idea_id}')
# @has_permission(Permissions.DELETE_IDEA)
async def delete_idea(idea_id: int,db: Session = Depends(get_db)):
    idea_repo = IdeaRepository(db)
    await idea_repo.delete_idea(int(idea_id))
    return {"message": f"Idea id {idea_id} is deleted successfully"}


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

    
@router.get("/files/download")
async def download_multiple_ideas_files(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Download files from multiple ideas as a ZIP file
    """
    idea_repo = IdeaRepository(db)
    idea_ids = await idea_repo.get_all_ideas_ids()
    
    # Create in-memory zip file
    zip_io = BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
        files_found = False
        for idea_id in idea_ids:
            try:
                idea = await idea_repo.get_raw_idea_by_id(idea_id)
                if not idea:
                    print(f"Idea {idea_id} not found")
                
                if not idea.files:
                    print(f"Idea {idea.id} has no files")
                    continue
                    
                for file in idea.files:
                    file_path = Path(__file__).parents[3] / file.filelocation
                    if file_path.exists():
                        safe_title = "".join(c for c in idea.title if c.isalnum() or c in " _-").strip()
                        safe_title = safe_title.replace(" ", "_")[:50]  # Limit length and replace spaces
                        archive_path = f"idea_{idea.id}_{safe_title}/{file.filename}"
                        zip_file.write(file_path, arcname=archive_path)
                        files_found = True
            except Exception as e:
                # Log any errors
                print(f"Error processing idea {idea_id}: {str(e)}")

                
        if not files_found:
            # Add a readme file if no files were found
            zip_file.writestr("README.txt", "No files were found for the selected ideas.")
    
    # Reset file pointer
    zip_io.seek(0)
    
    # Return the zip file as a streaming response
    return StreamingResponse(
        zip_io,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=ideas_files.zip"
        }
    )


@router.get("/{idea_id}/reports", status_code=status.HTTP_200_OK)
async def get_all_idea_reports(idea_id: int, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    idea_repo = IdeaRepository(db)
    reports = await idea_repo.get_idea_reports(idea_id)
    reports_response = [report.to_dict() for report in reports]
    return reports_response
    

@router.post("/{idea_id}/reports")
async def report_idea(
    idea_id: int, 
    report_request: ReportRequest, 
    current_user: CurrentUser, 
    db: AsyncSession = Depends(get_db)
):
    idea_repo = IdeaRepository(db)
    # Set the user_id and idea_id from the path and current user
    report_data = IdeaReportCreate(
        user_id = current_user.id,
        idea_id = idea_id,
        reason = report_request.reason
    )
    await idea_repo.report_idea(report_data)
    return {"detail": "Idea reported successfully"}


@router.delete("/{idea_id}/reports/{report_id}")
async def delete_idea_report(idea_id: int, report_id: int, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    idea_repo = IdeaRepository(db)
    message = await idea_repo.delete_report_idea(report_id)
    return {"detail": message}