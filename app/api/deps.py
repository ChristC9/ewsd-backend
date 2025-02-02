from typing import Annotated, Optional
from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from jose import jwt, JWTError

from app.models.user_model import User as UserModel
from app.repositories import users as user_repo
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
    
    user = await user_repo.get_user(db=db, username=username)
    if user is None:
        raise credentials_exception
    
    return user


CurrentUser = Annotated[UserModel, Depends(get_current_user)]
OptionalCurrentUser = Annotated[Optional[UserModel], Depends(get_current_user)]