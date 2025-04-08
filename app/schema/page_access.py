from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PageAccessCreate(BaseModel):
    pagename: str
    accessedby: int
    browsername: Optional[str] = None

class PageAccessResponse(BaseModel):
    id: int
    pagename: str
    accessedby: int
    accessedon: datetime
    browsername: Optional[str] = None
    
    class Config:
        from_attributes = True