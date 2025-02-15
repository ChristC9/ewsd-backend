from hmac import new
from tkinter import N
from click import Option
from pydantic import BaseModel, EmailStr
from typing import Optional

from datetime import datetime


class ForgetPasswordInitiateRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str


class OtpCreate(BaseModel):
    user_id: int
    otp: str
    expires_at: datetime


class OtpUpdate(BaseModel):
    otp: Optional[str] = None
    is_used: Optional[bool] = None
    expires_at: Optional[datetime] = None