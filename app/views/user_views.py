from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..schema.schema import UserCreate, UserLogin,RefreshToken
from datetime import datetime
from ..models.user_model import User as UserModel
from fastapi.security import OAuth2PasswordBearer
from ..auth.authentication import (
    authenticate_user,
)
from ..utils.tokens import get_access_token, get_refresh_token
from jose import jwt, JWTError
import bcrypt
from ..config import settings
from ..database import session_local

secret_key = settings.SECRET_KEY
algorithm = settings.ALGORITHM



def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db_user = UserModel(
        firstname=user.firstname,
        lastname=user.lastname,
        username=user.username,
        password=hashed_password,
        email= user.email if user.email else None,
        role=user.role,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_user)
    await db.commit()
    db.refresh(db_user)
    return db_user

def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

def read_all_users(db: Session = Depends(get_db)):
    return db.query(UserModel).all()


async def login(credentials: UserLogin, db: Session = Depends(get_db)):

    user = authenticate_user(db, credentials.username, credentials.password)
    print(user)
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


oauth2scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")
async def refresh_token(
    token: RefreshToken,
    db: Session = Depends(get_db)
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
        user = db.query(UserModel).filter(UserModel.username == username).first()
        
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
    
async def get_current_user(
        token: str = Depends(oauth2scheme),
        db: Session = Depends(get_db)
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
    

    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    return current_user