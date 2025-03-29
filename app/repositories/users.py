from calendar import c
from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import bcrypt
import traceback
from datetime import datetime, timezone
from app.schema.schema import UserCreate, UserListRequest
from app.models.user_model import User
from app.models.roles_model import Role
from app.models.department_model import Department
from app.utils.helpers import compute_pagination


class UserRepository:

    def __init__(self,db: AsyncSession):
        self.db = db


    async def get_user(self,username: str = None, user_id: int = None, email: str = None) -> User:

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


    async def get_all_users(self, filter_params: UserListRequest) -> tuple[list[User], dict]:
        """Get all users by filter"""
        query = (
            select(User)
        )
        if filter_params.search:
            search_term = f"%{filter_params.search}%"
            query = query.where(
            (User.firstname.ilike(search_term)) | 
            (User.lastname.ilike(search_term)) |
            (User.username.ilike(search_term))
            )
        if filter_params.department_id:
            query = query.where(User.department_id == filter_params.department_id)
        
        offset = (filter_params.page - 1) * filter_params.limit
        query = query.offset(offset).limit(filter_params.limit)
        result = await self.db.execute(query)
        users = result.unique().scalars().all()

        total_query = (
            select(func.count(User.id))
        )
        if filter_params.search:
            search_term = f"%{filter_params.search}%"
            total_query = total_query.where(
            (User.firstname.ilike(search_term)) | 
            (User.lastname.ilike(search_term)) |
            (User.username.ilike(search_term)) |
            ((User.firstname + ' ' + User.lastname).ilike(search_term))
            )
        if filter_params.department_id:
            total_query = total_query.where(User.department_id == filter_params.department_id)
        
        total_result = await self.db.execute(total_query)
        total = total_result.unique().scalar_one_or_none()

        pagination = compute_pagination(total, filter_params.page, filter_params.limit)
        return users, pagination


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
        except OperationalError:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)
        except SQLAlchemyError:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)
        except Exception:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)

    async def update_user_password(self, user_id: int, password: str) -> User:
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            query = update(User).where(User.id == user_id).values(password=hashed_password)
            await self.db.execute(query)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)

    async def delete_user(self, user_id:int) -> bool:

        try:
            user_to_delete = await self.get_user(user_id=user_id)
            await self.db.delete(user_to_delete)
            await self.db.commit()
            return True
        except SQLAlchemyError:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)
        
    async def disable_user(self, user_id: int) -> User:
    
        try:
            user = await self.get_user(user_id=user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
                
            user.isdisabled = True
            user.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)

    async def enable_user(self, user_id: int) -> User:
        
        try:
            user = await self.get_user(user_id=user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
                
            user.isdisabled = False
            user.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)
        

    async def get_mails_by_role(self, role_name: str, department_id: int = None) -> list[str]:
        try:
            query = (
                select(User.email)
                .join(Role, User.role_id == Role.id)
                .join(Department, User.department_id == Department.id)
                .where(Role.name == role_name and Department.id == department_id)
            )
            result = await self.db.execute(query)
            user_mails = result.unique().scalars().all()
        
            return user_mails
        except Exception:
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)