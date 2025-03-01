from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
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

        

    async def get_user(self, *, username: str = None, user_id: int = None, email: str = None) -> User:
        if username is not None:
            query = select(User).where(User.username == username)
        elif user_id is not None:
            query = select(User).where(User.id == user_id)
        elif email is not None:
            query = select(User).where(User.email == email)
        else:
            raise ValueError("Either username or user_id must be provided")

        result = await self.db.execute(query)
        user = result.unique().scalar_one_or_none()
        return user


    async def get_all_users(self) -> list[User]:
        query = select(User)
        result = await self.db.execute(query)
        users = result.unique().scalars().all()
        return users


    async def create_user(self, user: UserCreate) -> User:
        try:
            hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            default_hashed_password = bcrypt.hashpw(user.default_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            db_user = User(
                firstname=user.firstname,
                lastname=user.lastname,
                username=user.username,
                default_pwd = default_hashed_password,
                password=hashed_password,
                email= user.email if user.email else None,
                department_id=user.department_id,
                role_id=user.role_id
            )
            print(db_user)

            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            await self.db.refresh(db_user, ['role', 'department'])
            return db_user
        except Exception as e:
            await self.db.rollback()
            print("User Creation Error is " + str(e))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating user")
    
    async def update_user(self, user_id: int, user_data: UserCreate) -> User:
        try:
            user = await self.get_user(user_id=user_id)
            for k, v in user_data.model_dump(exclude_unset=True).items():
                setattr(user, k, v)
            user.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except OperationalError as e:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail="DB error occurred")
        except SQLAlchemyError as e:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail="DB error occurred")
        except Exception as e:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)

    async def update_user_password(self, user_id: int, password: str) -> User:
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            query = update(User).where(User.id == user_id).values(password=hashed_password)
            await self.db.execute(query)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail="DB error occurred")

    async def delete_user(self, user_id:int) -> bool:

        try:
            user_to_delete = await self.get_user(user_id=user_id)
            await self.db.delete(user_to_delete)
            await self.db.commit()
            return True
        except:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)