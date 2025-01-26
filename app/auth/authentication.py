from ..models.user_model import User
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, UTC
from ..utils.helpers import verify_password
from jose import jwt
from ..config import settings

secret_key = settings.SECRET_KEY
algorithm = settings.ALGORITHM


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_token(data: dict, expires_delta:timedelta)-> str:
    
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)
