from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.models.department_model import Department
from app.schema.schema import DepartmentCreate, DepartmentUpdate
from fastapi import HTTPException, status
from typing import List, Dict, Optional, Tuple
import traceback

from app.utils.helpers import compute_pagination
from app.schema.pagination import PaginationRequest


class DepartmentRepository:

    def __init__(self, db: Session):
        self.db = db

    
    async def create_department(self, department: DepartmentCreate) -> Department:
        
        
        try:
            new_department = Department(
                name = department.name,
                created_by = department.created_by,
                created_at = datetime.now(timezone.utc),
                updated_at = datetime.now(timezone.utc)
            )
            self.db.add(new_department)
            await self.db.commit()
            await self.db.refresh(new_department)
            return new_department
        except Exception as e:
            await self.db.rollback()
            print("Department Creation Error is " + str(e))        
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating department")


    async def get_all_departments(self, pagination: Optional[PaginationRequest] = None) -> Tuple[List[Department], Dict]:
        """Get all departments with optional pagination"""
        try:
            # Base query
            query = select(Department)
            
            # Count total for pagination
            count_query = select(func.count(Department.id))
            count_result = await self.db.execute(count_query)
            total = count_result.scalar_one_or_none() or 0
            
            
            if pagination:
                offset = (pagination.page - 1) * pagination.limit
                query = query.offset(offset).limit(pagination.limit)
                pagination_info = compute_pagination(total, pagination.page, pagination.limit)
            
            result = await self.db.execute(query)
            departments = result.scalars().all()
            
            return departments, pagination_info
        
        except Exception as e:
            tb_str = traceback.format_exc()
            print(f"Error fetching departments: {str(e)}\n{tb_str}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                               detail="Error fetching departments")
    

    async def get_department_by_id(self, department_id: int) -> Department:
        """Get a department by ID"""
        try:
            query = select(Department).where(Department.id == department_id)
            result = await self.db.execute(query)
            department = result.scalar_one_or_none()
            
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Department with ID {department_id} not found"
                )
            
            return department
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            tb_str = traceback.format_exc()
            print(f"Error fetching department: {str(e)}\n{tb_str}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                               detail="Error fetching department")
    

    async def update_department(self, department_id: int, department_data: DepartmentUpdate) -> Department:
        """Update a department"""
        try:
            # Check if department exists
            query = select(Department).where(Department.id == department_id)
            result = await self.db.execute(query)
            department = result.scalar_one_or_none()
            
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Department with ID {department_id} not found"
                )
            
            # Update department
            department.name = department_data.name
            department.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(department)
            return department
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            print(f"Error updating department: {str(e)}\n{tb_str}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                               detail="Error updating department")
    
    async def delete_department(self, department_id: int) -> bool:
        """Delete a department"""
        try:
            # Check if department exists
            query = select(Department).where(Department.id == department_id)
            result = await self.db.execute(query)
            department = result.scalar_one_or_none()
            
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Department with ID {department_id} not found"
                )
            
            # Delete department
            delete_stmt = delete(Department).where(Department.id == department_id)
            await self.db.execute(delete_stmt)
            await self.db.commit()
            
            return True
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            print(f"Error deleting department: {str(e)}\n{tb_str}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                               detail="Error deleting department")