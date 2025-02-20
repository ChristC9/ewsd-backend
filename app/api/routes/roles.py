from fastapi import APIRouter,status,Depends
from app.schema.schema import RoleBase,RoleCreate
from sqlalchemy.orm import Session
from app.database import get_db
from ..deps import CurrentUser, get_current_user
from app.repositories.roles import RoleRepository
from app.auth.permissions import Permissions, has_permission


router = APIRouter()


@router.post('/',response_model=RoleBase, status_code=status.HTTP_201_CREATED)
async def create_role(role:RoleCreate, db: Session = Depends(get_db)):
    
    role_repo = RoleRepository(db)
    return await role_repo.create_role(role)

@router.get('/',response_model=list[RoleBase],status_code=status.HTTP_200_OK)
@has_permission(Permissions.READ_ROLE)
async def get_roles(current_user: CurrentUser, db: Session = Depends(get_db)):
    
    role_repo = RoleRepository(db)
    result = await role_repo.get_role()
    return result

@router.get('/{role_id}',response_model=RoleBase,status_code=status.HTTP_200_OK)
@has_permission(Permissions.READ_ROLE)
async def get_role_by_id(role_id:int, db: Session = Depends(get_db)):
    
    role_repo = RoleRepository(db)
    return role_repo.get_role_by_id(role_id)

@router.patch('/{role_id}', response_model=RoleBase, status_code=status.HTTP_200_OK)
@has_permission(Permissions.UPDATE_ROLE)
async def update_role(role_id:int,role_data: RoleBase, db: Session = Depends(get_db)):
    
    role_repo = RoleRepository(db)
    return role_repo.update_role(role_id, role_data)

@router.delete('/{role_id}', status_code=status.HTTP_204_NO_CONTENT)
@has_permission(Permissions.DELETE_ROLE)
async def delete_role(role_id:int, db: Session = Depends(get_db)):
    
    role_repo = RoleRepository(db)
    return role_repo.delete_role(role_id)