from fastapi import APIRouter, Depends, HTTPException, status, Query, status
from typing import List, Optional, Annotated
from app.schema.schema import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentListRequest,
    DepartmentListResponse
)
from app.api.deps import CurrentUser
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories.departments import DepartmentRepository
from app.auth.permissions import Permissions, has_permission


router = APIRouter()


@router.post('/',response_model=DepartmentCreate, status_code=status.HTTP_201_CREATED)
# @has_permission(Permissions.CREATE_DEPARTMENT)
async def create_department(department:DepartmentCreate, db: Session = Depends(get_db)):
    
    department_repo = DepartmentRepository(db)
    return await department_repo.create_department(department)


@router.get("/", response_model=DepartmentListResponse)
async def get_all_departments(
    params: Annotated[DepartmentListRequest, Query()],
    db: AsyncSession = Depends(get_db)
):
    """Get all departments"""
    department_repo = DepartmentRepository(db)
    departments, pagination = await department_repo.get_all_departments(params)
    
    return DepartmentListResponse(
        data=departments,
        pagination=pagination
    )

@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a department by ID"""
    department_repo = DepartmentRepository(db)
    department = await department_repo.get_department_by_id(department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    return department



@router.put("/{department_id}", response_model=DepartmentResponse)
@has_permission(Permissions.UPDATE_DEPARTMENT)
async def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Update a department"""
    department_repo = DepartmentRepository(db)
    department = await department_repo.update_department(department_id, department_data)
    return department

@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
@has_permission(Permissions.DELETE_DEPARTMENT)
async def delete_department(
    department_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Delete a department"""
    department_repo = DepartmentRepository(db)
    await department_repo.delete_department(department_id)
    return None