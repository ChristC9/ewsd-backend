import select
from unittest import result
from ..models.user_model import User
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta, timezone
from ..utils.helpers import verify_password
from jose import jwt
from ..config import settings
from app.repositories import users as user_repo

secret_key = settings.SECRET_KEY
algorithm = settings.ALGORITHM


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    user = await user_repo.get_user(db, username=username)
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_token(data: dict, expires_delta:timedelta)-> str:
    
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)
