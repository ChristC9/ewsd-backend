from pydantic import BaseModel, UUID4, Field
from datetime import datetime, date
from typing import Optional, List

from app.schema.pagination import PaginationRequest, PaginationResponse

class UserBase(BaseModel):

    firstname: str
    lastname: str
    email: Optional[str] = None
    username: str
    default_pwd: str
    password: str
    isdisabled: bool = False
    islocked: bool = False
    lastlogin: Optional[datetime] = None


    class Config:
        orm_mode = True


class UserListRequest(PaginationRequest):
    search: Optional[str] = None
    department_id: Optional[int] = None
    role_id: Optional[int] = None


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

class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class DepartmentResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
        
class UserResponse(UserBase):

    id: int
    role: RoleResponse
    department: DepartmentResponse
    created_at: datetime
    updated_at: datetime
    password: str = Field(exclude=True)
    default_pwd: str = Field(exclude=True)
    class Config:
        from_attributes = True
class CommentBase(BaseModel):
    comment: str
    ispostedanon: bool = False

class LikeBase(BaseModel):
    isliked: bool = True

class FileBase(BaseModel):
    filename: str
    filetype: str

# Create request schemas
class CommentCreate(CommentBase):
    pass

class LikeCreate(LikeBase):
    pass

class FileCreate(FileBase):
    pass

# Response schemas
class UserBasic(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class CommentResponse(CommentBase):
    id: int
    commentuid: UUID4
    ideaid: int
    postedby: int
    postedon: date
    user: Optional[UserBasic]

    class Config:
        from_attributes = True

class LikeResponse(LikeBase):
    id: int
    likeuid: UUID4
    ideaid: int
    postedby: int
    postedon: date
    user: Optional[UserBasic]

    class Config:
        from_attributes = True

class FileResponse(FileBase):
    fileid: int
    fileguid: UUID4
    ideaid: int

    class Config:
        from_attributes = True

class IdeaResponse(BaseModel):
    id: int
    ideaguid: UUID4
    title: str
    description: Optional[str]
    postedby: int
    postedon: date
    ispostedanon: bool
    isactived: bool
    user: Optional[UserBasic]
    files: List[FileResponse] = []
    comments: List[CommentResponse] = []
    likes: List[LikeResponse] = []

    class Config:
        from_attributes = True

# Form data schemas for requests
class IdeaCreate(BaseModel):
    title: str
    description: Optional[str] = None
    is_posted_anon: bool = False

class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_posted_anon: Optional[bool] = None

# Response schemas for paginated results
class PaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[IdeaResponse]

# Statistics schemas
class IdeaStats(BaseModel):
    total_likes: int
    total_comments: int
    total_files: int

class IdeaDetailResponse(IdeaResponse):
    stats: IdeaStats


class UserListResponse(BaseModel):
    data: List[UserResponse]
    pagination: PaginationResponse