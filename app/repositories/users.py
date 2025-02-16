from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
from sqlalchemy.orm import Session
import bcrypt
import traceback

from datetime import datetime, timezone

from app.schema.schema import UserCreate
from app.models.user_model import User

class UserRepository:

    def __init__(self,db:Session):
        self.db = db

        

    async def get_user(db: AsyncSession, *, username: str = None, user_id: int = None) -> User:
        if username is not None:
            query = select(User).where(User.username == username)
        elif user_id is not None:
            query = select(User).where(User.id == user_id)
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
    
    async def update_user(self,db: AsyncSession, user_id: int, user_data: UserCreate) -> User:
        try:
            user = await self.get_user(db, user_id=user_id)
            for k, v in user_data.model_dump(exclude_unset=True).items():
                setattr(user, k, v)
            user.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(user)
            return user
        except OperationalError as e:
            await db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail="DB error occurred")
        except SQLAlchemyError as e:
            await db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail="DB error occurred")
        except Exception as e:
            await db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)

    async def delete_user(self,db:AsyncSession, user_id:int) -> bool:

        try:
            user_to_delete = await self.get_user(db, user_id=user_id)
            await db.delete(user_to_delete)
            await db.commit()
            return True
        except:
            await db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)