from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    firstname: str
    lastname: str
    email: Optional[str] = None
    username: str

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    password: str
    role: str

class UserResponse(UserBase):
    id: int
    # password: str
    role: str
    created_at: datetime
    updated_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserLogin(BaseModel):
    username: str
    password: str

class RefreshToken(BaseModel):
    refresh_token: str


class RoleBase(BaseModel):

    id: int
    name: str
    created_by: UserBase
    created_at: datetime
    updated_at: datetime