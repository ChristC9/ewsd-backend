from pydantic import BaseModel, UUID4, Field
from typing import Optional
from datetime import date

class CommentBase(BaseModel):
    comment: str
    ispostedanon: bool = False

class CommentCreate(CommentBase):
    ideaid: int
    # Removed postedby field since it will come from the authenticated user

class CommentResponse(CommentBase):
    id: int
    commentuid: UUID4
    ideaid: int
    postedby: int
    postedon: date
    username: Optional[str] = None  # From the related User

    class Config:
        from_attributes = True