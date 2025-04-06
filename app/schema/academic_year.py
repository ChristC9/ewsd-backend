from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from datetime import date, datetime
from app.schema.pagination import PaginationResponse, PaginationRequest

class AcademicYearBase(BaseModel):
    name: str
    start_date: date
    end_date: date
    is_active: bool = True
    is_current: Optional[bool] = False
    submission_end_date: date
    final_closure_date: date

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
        
    @validator('submission_end_date')
    def submission_end_date_validation(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('submission_end_date cannot be before start_date')
        return v
        
    @validator('final_closure_date')
    def final_closure_date_validation(cls, v, values):
        if 'submission_end_date' in values and v < values['submission_end_date']:
            raise ValueError('final_closure_date must be after submission_end_date')
        if 'end_date' in values and v > values['end_date']:
            raise ValueError('final_closure_date cannot be after end_date')
        return v

class AcademicYearCreate(AcademicYearBase):
    pass

class AcademicYearUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    is_current: Optional[bool] = None
    submission_end_date: Optional[date] = None
    final_closure_date: Optional[date] = None

class AcademicYearResponse(AcademicYearBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AcademicYearListRequest(PaginationRequest):
    search: Optional[str] = None
    active_only: Optional[bool] = None

class AcademicYearListResponse(BaseModel):
    data: List[AcademicYearResponse]
    pagination: PaginationResponse

class SubmissionStatusResponse(BaseModel):
    can_submit: bool
    is_final_closure: bool
    current_date: date
    submission_end_date: Optional[date] = None
    final_closure_date: Optional[date] = None
    days_left_for_submission: Optional[int] = None
    message: str