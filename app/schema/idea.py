from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, ByteString, List

from app.schema.pagination import PaginationResponse, PaginationRequest

class IdeasListRequest(PaginationRequest):
    filter_category: Optional[List[int]] = Field(None, alias="filter[category]")
    sort_date: Optional[int] = Field(None, alias="sort[date]")
    search: Optional[str] = Field(None)
    filter_my: Optional[bool] = Field(None, alias="filter[my]")
    filter_popular: Optional[bool] = Field(None, alias="filter[popular]")
        

class IdeaResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    thumbnail: Optional[str]
    # likes_count: int
    # comments_count: int
    posted_by: str    # UserBasic
    posted_on: datetime

    class Config:
        orm_mode = True


class IdeaListResponse(BaseModel):
    data: list[IdeaResponse]
    pagination: PaginationResponse



