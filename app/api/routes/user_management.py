from time import sleep
import time
from unittest import result
from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from jose import jwt, JWTError
from typing import Annotated, Optional

from app.api.deps import CurrentUser, OptionalCurrentUser
from app.schema.schema import UserCreate, UserLogin, Token, RefreshToken, UserResponse
from app.models.user_model import User as UserModel
from app.repositories.users import UserRepository
from app.auth.authentication import (
    authenticate_user,
)
from app.utils.tokens import get_access_token, get_refresh_token
from app.config import settings
from app.database import get_db
from app.auth.permissions import has_permission, Permissions

secret_key = settings.SECRET_KEY
algorithm = settings.ALGORITHM

router = APIRouter()
token_router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@has_permission(Permissions.CREATE_USER)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    db_user =  await user_repo.create_user(user)
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
@has_permission(Permissions.READ_USER)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=list[UserResponse])
@has_permission(Permissions.READ_USER)
async def read_all_users(db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    db_users = await user_repo.get_all_users(db)
    return db_users


@router.post("/login", response_model=Token)
# async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
async def login(credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
            )

    access_token = get_access_token(user)
    refresh_token = get_refresh_token(user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@token_router.post("/refresh", response_model=RefreshToken)
async def refresh_token(
    token: RefreshToken,
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(token.refresh_token, secret_key, algorithms=[algorithm])
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=403,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        username = payload.get("sub")
        user_repo = UserRepository(db)
        user = await user_repo.get_user(db, username=username)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        access_token = get_access_token(user)
        refresh_token = get_refresh_token(user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    return current_user


@router.patch("/{user_id}", response_model=UserResponse)
@has_permission(Permissions.UPDATE_USER)
async def update_user(user_id: int, user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.update_user(db, user_id, user_data)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@has_permission(Permissions.DELETE_USER)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    deleted_user = await user_repo.delete_user(db, user_id)
    return deleted_user