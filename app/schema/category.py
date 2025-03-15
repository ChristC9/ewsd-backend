from pydantic import BaseModel
from typing import Optional

from datetime import datetime

from app.schema.pagination import PaginationRequest, PaginationResponse

class CategoryCreateRequest(BaseModel):
    name: str

class CategoryCreate(CategoryCreateRequest):
    created_by: str

class CategoryBase(CategoryCreate):
    id: int
    created_at: datetime


class CategroyListRequest(PaginationRequest):
   search: Optional[str] = None


class CategoryListResponse(BaseModel):
    data: list[CategoryBase]
    pagination: PaginationResponse