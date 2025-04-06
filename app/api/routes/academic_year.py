from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional

from app.database import get_db
from app.api.deps import CurrentUser
from app.auth.permissions import Permissions, has_permission
from app.repositories.academic_year import AcademicYearRepository
from app.schema.academic_year import (
    AcademicYearCreate, 
    AcademicYearUpdate, 
    AcademicYearResponse,
    AcademicYearListResponse,
    AcademicYearListRequest,
    SubmissionStatusResponse
)

router = APIRouter()

@router.get("/", response_model=AcademicYearListResponse)
async def get_all_academic_years(
    params: Annotated[AcademicYearListRequest, Query()],
    db: AsyncSession = Depends(get_db)
):
    """Get all academic years with optional filtering"""
    academic_year_repo = AcademicYearRepository(db)
    academic_years, pagination = await academic_year_repo.get_all_academic_years(params)
    
    return AcademicYearListResponse(
        data=academic_years,
        pagination=pagination
    )
    
@router.get("/current", response_model=AcademicYearResponse)
async def get_current_academic_year(
    db: AsyncSession = Depends(get_db)
):
    """Get the current academic year"""
    academic_year_repo = AcademicYearRepository(db)
    academic_year = await academic_year_repo.get_current_academic_year()
    
    if not academic_year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No current academic year set"
        )
        
    return academic_year

@router.get("/submission-status", response_model=SubmissionStatusResponse)
async def check_submission_status(
    db: AsyncSession = Depends(get_db)
):
    """Check if idea submission is still open based on the current academic year"""
    academic_year_repo = AcademicYearRepository(db)
    return await academic_year_repo.check_submission_status()

@router.get("/{academic_year_id}", response_model=AcademicYearResponse)
async def get_academic_year(
    academic_year_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get an academic year by ID"""
    academic_year_repo = AcademicYearRepository(db)
    academic_year = await academic_year_repo.get_academic_year_by_id(academic_year_id)
    
    if not academic_year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academic year with ID {academic_year_id} not found"
        )
        
    return academic_year

@router.post("/", response_model=AcademicYearResponse, status_code=status.HTTP_201_CREATED)
# @has_permission(Permissions.CREATE_SETTINGS)
async def create_academic_year(
    academic_year: AcademicYearCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Create a new academic year"""
    academic_year_repo = AcademicYearRepository(db)
    academic_year = await academic_year_repo.create_academic_year(academic_year, username=current_user.username)
    return academic_year


@router.put("/{academic_year_id}", response_model=AcademicYearResponse)
# @has_permission(Permissions.UPDATE_SETTINGS)
async def update_academic_year(
    academic_year_id: int,
    academic_year_data: AcademicYearUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Update an academic year"""
    academic_year_repo = AcademicYearRepository(db)
    return await academic_year_repo.update_academic_year(academic_year_id, academic_year_data)

@router.delete("/{academic_year_id}", status_code=status.HTTP_204_NO_CONTENT)
# @has_permission(Permissions.DELETE_SETTINGS)
async def delete_academic_year(
    academic_year_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Delete an academic year"""
    academic_year_repo = AcademicYearRepository(db)
    await academic_year_repo.delete_academic_year(academic_year_id)
    return None