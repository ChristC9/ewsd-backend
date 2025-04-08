from pydantic import BaseModel, UUID4, Field
from datetime import date
from typing import Optional

class LikeBase(BaseModel):
    ideaid: int
    isliked: bool = False
    isdisliked: bool = False
    
class LikeCreate(LikeBase):
    pass

class LikeResponse(LikeBase):
    id: int
    likeuid: UUID4
    postedby: int
    postedon: Optional[date] = None
    
    class Config:
        from_attributes = True