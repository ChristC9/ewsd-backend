from ast import For
from time import sleep
import time
from unittest import result
from fastapi import Depends, HTTPException, APIRouter, status
from fastapi import security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from jose import jwt, JWTError
from typing import Annotated, Optional
from datetime import datetime, timezone, timedelta

from app.api.deps import CurrentUser, OptionalCurrentUser
from app.models.security import Otp
from app.schema.schema import UserCreate, UserLogin, Token, RefreshToken, UserResponse
from app.schema.security import ForgetPasswordInitiateRequest, ResetPasswordRequest, OtpCreate, OtpUpdate
from app.models.user_model import User as UserModel
from app.repositories import (
    users as user_repo,
    security as security_repo
)
from app.auth.authentication import (
    authenticate_user,
)
from app.utils.tokens import get_access_token, get_refresh_token
from app.utils.helpers import generate_otp_code, send_otp_email
from app.config import settings
from app.database import get_db

secret_key = settings.SECRET_KEY
algorithm = settings.ALGORITHM

router = APIRouter()
token_router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await user_repo.create_user(db, user)
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_repo.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=list[UserResponse])
async def read_all_users(db: AsyncSession = Depends(get_db)):
    db_users = await user_repo.get_all_users(db)
    return db_users


@router.post("/login", response_model=Token)
# async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
async def login(credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, credentials.username, credentials.password)
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


@router.post("/forget-password/initiate")
async def initiate_password_reset(
    initiateRequest: ForgetPasswordInitiateRequest,
    db: AsyncSession = Depends(get_db),
):
    # get user
    user = await user_repo.get_user(db, email=initiateRequest.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # generate otp
    otp_code = generate_otp_code(length=6)
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

    # save otp to db
    otp_data_object = await security_repo.get_otp(db, user.id, is_used=False)
    if otp_data_object:
        otpUpdate = OtpUpdate(otp=otp_code, expires_at=expire_at, is_used=False)
        otp = await security_repo.update_otp_by_model(db, otpUpdate, otp_data_object)
    else:
        otpCreate = OtpCreate(user_id=user.id, otp=otp_code, expires_at=expire_at)
        otp = await security_repo.create_otp(db, otpCreate)
    
    # send otp to user
    # TODO: send otp to user
    send_otp_email(to_email=initiateRequest.email, otp_code=otp_code)
    print(otp.colotp)
    return {"detail": f"OTP sent successfully to {initiateRequest.email}"}


@router.post("/forget-password/reset")
async def reset_password(
    resetRequest: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    # get user
    user = await user_repo.get_user(db, email=resetRequest.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = user.id
    
    # get otp
    otp_data_object = await security_repo.get_otp(db, user.id, is_used=False)
    if not otp_data_object:
        raise HTTPException(status_code=404, detail="OTP not found")
    
    # validate otp
    if otp_data_object.colotp != resetRequest.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # mark otp as used
    otpUpdate = OtpUpdate(is_used=True)
    await security_repo.update_otp_by_model(db, otpUpdate, otp_data_object)

    # update password
    await user_repo.update_user_password(db, user_id, resetRequest.new_password)
    
    return {"detail": "Password reset successfully."}