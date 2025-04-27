from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.schema.pagination import PaginationResponse, PaginationRequest
from app.schema.category import CategoryBase
from app.schema.schema import DepartmentBase
from app.schema.comment import CommentResponse


class FileResponse(BaseModel):
    id: int
    filename: str
    filetype: str
    filelocation: str

    class Config:
        from_attributes = True


class IdeasListRequest(PaginationRequest):
    filter_category: Optional[List[int]] = Field(None, alias="filter[category]")
    sort_by_date: Optional[int] = Field(None, alias="sort[date]")
    sort_by_likes: Optional[int] = Field(None, alias="sort[likes]")
    sort_by_popularity: Optional[int] = Field(None, alias="sort[popularity]")
    sort_by_most_viewed: Optional[int] = Field(None, alias="sort[most_viewed]")
    search: Optional[str] = Field(None)
    filter_my: Optional[bool] = Field(None, alias="filter[my]")
    filter_reported: Optional[bool] = Field(None, alias="filter[reported]")
    filter_department: Optional[List[int]] = Field(None, alias="filter[department]")

class IdeaResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    likes_count: int
    dislikes_count: int
    comments_count: int
    views_count: int
    reports_count: Optional[int] = 0
    thumbnail: Optional[Any] = None  # Will store Base64 encoded string
    posted_by: Dict[str, Any]
    posted_on: datetime
    department: DepartmentBase
    category: CategoryBase
    files: List[FileResponse] = []
    comments: List[CommentResponse] = []
    current_user_reaction: Optional[str] = None

    class Config:
        from_attributes = True

class IdeaListResponse(BaseModel):
    data: list[IdeaResponse]
    pagination: PaginationResponse


class ReportRequest(BaseModel):
    reason: Optional[str] = None

class IdeaReportCreate(BaseModel):
    user_id: int
    idea_id: int
    reason: Optional[str] = None
