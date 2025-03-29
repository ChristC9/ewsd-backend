from typing import Annotated, Optional
from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from jose import jwt, JWTError

from app.models.user_model import User as UserModel
from app.repositories.users import UserRepository
from app.utils.tokens import get_access_token, get_refresh_token
from app.config import settings
from app.database import get_db

secret_key = settings.SECRET_KEY
algorithm = settings.ALGORITHM
oauth2scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


async def get_current_user(
        token: str = Depends(oauth2scheme),
        db: AsyncSession = Depends(get_db)
)-> UserModel:
    
    credentials_exception = HTTPException(
        status_code= 401,
        detail= "Could not validate credentials",
        headers= {"WWW-Authenticate": "Bearer"}

    )
    try:

        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username : str = payload.get("sub")
        token_type : str = payload.get("type")

        if not username or token_type != "access":
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    user_repo = UserRepository(db)
    user = await user_repo.get_user(username=username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_qa_manager(
    current_user: UserModel = Depends(get_current_active_user)
) -> UserModel:
    if current_user.role.name != "QA_MANAGER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="QA Manager access required"
        )
    return current_user

async def get_current_qa_staff(
    current_user: UserModel = Depends(get_current_active_user)
) -> UserModel:
    if current_user.role.name not in ["QA Manager", "QA Staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="QA Staff access required"
        )
    return current_user

async def get_user_role(current_user: UserModel = Depends(get_current_user)) -> str:
    return current_user.role.name

async def check_user_role(role_name: str, current_user: UserModel = Depends(get_current_user)) -> bool:
    return current_user.role.name == role_name

CurrentUser = Annotated[UserModel, Depends(get_current_user)]
OptionalCurrentUser = Annotated[Optional[UserModel], Depends(get_current_user)]


# def check_user_not_disabled():
    
#     async def dependency(current_user: CurrentUser = Depends(get_current_user)):
#         if current_user.isdisabled:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Your account is disabled. You cannot perform this action."
#             )
#         return current_user
    
#     return dependency