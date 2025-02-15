from turtle import up
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError

import bcrypt
import traceback

from datetime import datetime, timezone

from app.schema.schema import UserCreate
from app.models.user_model import User


async def get_user(db: AsyncSession, *, username: str = None, user_id: int = None, email: str = None) -> User:
    if username is not None:
        query = select(User).where(User.username == username)
    elif user_id is not None:
        query = select(User).where(User.id == user_id)
    elif email is not None:
        query = select(User).where(User.email == email)
    else:
        raise ValueError("Either username or user_id must be provided")

    result = await db.execute(query)
    user = result.unique().scalar_one_or_none()
    return user


async def get_all_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    try:
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db_user = User(
            firstname=user.firstname,
            lastname=user.lastname,
            username=user.username,
            password=hashed_password,
            email= user.email if user.email else None,
            role=user.role,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return db_user
    except IntegrityError as e:
        await db.rollback()
        tb_str = traceback.format_exc()
        raise HTTPException(status_code=400, detail="Username already exists")
    except SQLAlchemyError as e:
        await db.rollback()
        tb_str = traceback.format_exc()
        raise HTTPException(status_code=400, detail="DB error occurred")
    except Exception as e:
        await db.rollback()
        tb_str = traceback.format_exc()
        raise HTTPException(status_code=400, detail=tb_str)


async def update_user_password(db: AsyncSession, user_id: int, password: str) -> User:
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query = update(User).where(User.id == user_id).values(password=hashed_password)
        await db.execute(query)
        await db.commit()
    except Exception as e:
        await db.rollback()
        tb_str = traceback.format_exc()
        raise HTTPException(status_code=400, detail="DB error occurred")