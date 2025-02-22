from pydantic import BaseModel
from typing import Optional

from datetime import datetime


class CategoryCreateRequest(BaseModel):
    name: str

class CategoryCreate(CategoryCreateRequest):
    created_by: str

class Category(CategoryCreate):
    id: int
    created_at: datetime



    