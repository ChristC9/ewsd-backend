from pydantic import BaseModel, Field, UUID4
from datetime import date
from typing import Optional, List

# Schema for creating a new Restriction
class RestrictionCreate(BaseModel):
    submission_date: date
    final_closure_date: date

# Schema for updating an existing Restriction
class RestrictionUpdate(BaseModel):
    submission_date: date
    final_closure_date: date

# Schema for returning a Restriction
class RestrictionResponse(BaseModel):
    id: int
    submission_date: date
    final_closure_date: date
    user_id: int
    
    class Config:
        from_attributes = True

# Schema for returning multiple Restrictions
class RestrictionListResponse(BaseModel):
    items: List[RestrictionResponse]
    total: int