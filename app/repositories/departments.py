from sqlalchemy.orm import Session
from datetime import datetime,timezone
from app.models.department_model import Department
from app.schema.schema import DepartmentCreate
from fastapi import HTTPException, status
from typing import List


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