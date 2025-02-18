from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):

    firstname: str
    lastname: str
    email: Optional[str] = None
    username: str
    default_password: str
    pasword: str

    class Config:
        orm_mode = True


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

    name: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class RoleCreate(BaseModel):
    name: str
    created_by: str

class UserCreate(UserBase):
    role_id: int
    department_id: int

class DepartmentBase(BaseModel):
    
    id: int
    name: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DepartmentCreate(BaseModel):
    name: str
    created_by: str
class UserResponse(UserBase):

    id: int
    role: RoleBase
    department: DepartmentBase
    created_at: datetime
    updated_at: datetime