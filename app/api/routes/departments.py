from fastapi import APIRouter,status,Depends
from app.schema.schema import DepartmentCreate
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.departments import DepartmentRepository
from app.auth.permissions import Permissions, has_permission


router = APIRouter()


@router.post('/',response_model=DepartmentCreate, status_code=status.HTTP_201_CREATED)
# @has_permission(Permissions.CREATE_DEPARTMENT)
async def create_department(department:DepartmentCreate, db: Session = Depends(get_db)):
    
    department_repo = DepartmentRepository(db)
    return await department_repo.create_department(department)


