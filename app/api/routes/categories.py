from calendar import c
from fastapi import Depends, HTTPException, APIRouter, status
from fastapi import security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from jose import jwt, JWTError
from typing import Annotated, Optional
from datetime import datetime, timezone, timedelta

from sqlmodel import all_

from app.api.deps import CurrentUser, OptionalCurrentUser
from app.models.category_model import Category
from app.repositories.categories import CategoryRepository
from app.schema.category import CategoryCreateRequest, CategoryCreate, Category
from app.auth.permissions import has_permission, Permissions

from app.database import get_db


router = APIRouter()

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
@has_permission(Permissions.CREATE_CATEGORY)
async def create_category(category: CategoryCreateRequest, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    category_repo = CategoryRepository(db)
    category = CategoryCreate(
        name = category.colname,
        created_by = current_user.username
    )
    db_category =  await category_repo.create_category(category)
    category_response = Category(**db_category.model_dump())
    return category_response

@router.get("/", response_model=list[Category])
@has_permission(Permissions.READ_CATEGORY)
async def get_all_categories(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    category_repo = CategoryRepository(db)
    result = await category_repo.get_all_categories()
    all_categories = []
    for category in result:
        category_response = Category(
            id = category.id,
            name = category.name,
            created_by = category.created_by,
            created_at = category.created_at
        )
        all_categories.append(category_response)
    return all_categories