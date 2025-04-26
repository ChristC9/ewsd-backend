from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from app.schema.pagination import PaginationResponse, PaginationRequest
from app.schema.schema import UserResponse

class UserActivity(BaseModel):
    user: UserResponse
    activity_count: int

class UsersActivityResponse(BaseModel):
    data: List[UserActivity]
    pagination: PaginationResponse

class BrowserUsage(BaseModel):
    browser_name: str
    usage_count: int
    usage_percentage: float

class MostUsedBrowsersResponse(BaseModel):
    data: List[BrowserUsage]
    total_page_accesses: int


class PageUsage(BaseModel):
    page_name: str
    access_count: int
    access_percentage: float

class MostUsedPagesResponse(BaseModel):
    data: List[PageUsage]
    total_page_accesses: int