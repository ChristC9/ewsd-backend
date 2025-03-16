from datetime import datetime
from re import A
from pydantic import BaseModel, Field
from typing import Optional, ByteString, List, Any

from app.schema.pagination import PaginationResponse, PaginationRequest
from app.schema.category import CategoryBase
from app.schema.schema import DepartmentBase


class FileResponse(BaseModel):
    id: int
    filename: str
    filetype: str

    class Config:
        from_attributes = True


class IdeasListRequest(PaginationRequest):
    filter_category: Optional[List[int]] = Field(None, alias="filter[category]")
    sort_by_date: Optional[int] = Field(None, alias="sort[date]")
    sort_by_likes: Optional[int] = Field(None, alias="sort[likes]")
    search: Optional[str] = Field(None)
    filter_my: Optional[bool] = Field(None, alias="filter[my]")
    filter_reported: Optional[bool] = Field(None, alias="filter[reported]")
    filter_department: Optional[List[int]] = Field(None, alias="filter[department]")


        
class IdeaResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    thumbnail: Optional[str]
    likes_count: int
    dislikes_count: int
    comments_count: int
    reports_count: Optional[int] = 0
    posted_by: dict
    posted_on: datetime
    category: CategoryBase
    department: DepartmentBase
    files: Optional[List[FileResponse]] = None

    class Config:
        orm_mode = True


class IdeaListResponse(BaseModel):
    data: list[IdeaResponse]
    pagination: PaginationResponse


class ReportRequest(BaseModel):
    reason: Optional[str] = None

class IdeaReportCreate(BaseModel):
    user_id: int
    idea_id: int
    reason: Optional[str] = None
