from calendar import c
from urllib import response
from fastapi import Depends, HTTPException, APIRouter, status, Query
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
from app.schema import pagination
from app.schema.category import CategoryCreateRequest, CategoryCreate, CategoryBase, CategoryListResponse, CategroyListRequest
from app.auth.permissions import has_permission, Permissions

from app.database import get_db


router = APIRouter()

@router.post("/", response_model=CategoryBase, status_code=status.HTTP_201_CREATED)
@has_permission(Permissions.CREATE_CATEGORY)
async def create_category(category: CategoryCreateRequest, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    category_repo = CategoryRepository(db)
    category = CategoryCreate(
        name = category.name,
        created_by = current_user.username
    )
    db_category =  await category_repo.create_category(category)
    category_response = CategoryBase(
        id = db_category.categoryid,
        name = db_category.categoryname,
        created_by = db_category.created_by,
        created_at = db_category.created_at
    )
    return category_response

@router.get("/", response_model=CategoryListResponse)
@has_permission(Permissions.READ_CATEGORY)
async def get_all_categories(filter_params: Annotated[CategroyListRequest, Query()], current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    category_repo = CategoryRepository(db)
    result, pagination = await category_repo.get_all_categories(filter_params)
    all_categories = []
    for category in result:
        category_response = CategoryBase(
            id = category.categoryid,
            name = category.categoryname,
            created_by = category.created_by,
            created_at = category.created_at
        )
        all_categories.append(category_response)
    all_categories_response = CategoryListResponse(
        data=all_categories,
        pagination=pagination
    )
    return all_categories_response


@router.patch("/{category_id}", response_model=CategoryBase)
@has_permission(Permissions.READ_CATEGORY)
async def update_category(category_id: int, category_name: str, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    category_repo = CategoryRepository(db)
    db_category = await category_repo.update_category(category_id, category_name)
    category_response = CategoryBase(
        id = db_category.categoryid,
        name = db_category.categoryid,
        created_by = db_category.created_by,
        created_at = db_category.created_at
    )
    return category_response


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
@has_permission(Permissions.DELETE_CATEGORY)
async def delete_category(category_id: int, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    category_repo = CategoryRepository(db)
    response = await category_repo.delete_category(category_id)
    return response