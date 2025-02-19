from sqlalchemy.orm import Session
from datetime import datetime,timezone
from app.models.roles_model import Role
from app.schema.schema import RoleBase, RoleCreate
from fastapi import HTTPException, status
from typing import List

class RoleRepository:

    def __init__(self, db: Session):
        self.db = db

    async def create_role(self, role: RoleCreate) -> Role:

        try:
            new_role = Role(
                name = role.name,
                created_by = role.created_by,
                created_at = datetime.now(timezone.utc),
                updated_at = datetime.now(timezone.utc)
            )
            print(new_role)
            self.db.add(new_role)
            await self.db.commit()
            await self.db.refresh(new_role)
            return new_role
        except Exception as e:
            self.db.rollback()
            print("Role Creation Error is " + str(e))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating role")
    
    async def get_role(self) -> List[Role]:
        roles = await self.db.query(Role).all()
        return roles
    
    async def get_role_by_id(self, role_id: int) -> Role:
        
        specific_role = await self.db.query(Role).filter(Role.id == role_id).first()
        if not specific_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        
        return specific_role
    
    async def get_role_by_name(self, role_name: str) -> Role:

        specific_role = await self.db.query(Role).filter(Role.name == role_name).first()
        if not specific_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        return specific_role
    
    async def update_role(self, role_id: int, role_data: RoleBase)->Role:

        role = await self.get_role_by_id(role_id)
        try:
            for k,v in role_data.model_dump(exclude_unset=True).items():
                setattr(role, k, v)
            role.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(role)
            return role
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error updating role")
    
    async def delete_role(self, role_id: int)->bool:

        role_to_delete = await self.get_role_by_id(role_id)

        try:
            await self.db.delete(role_to_delete)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting role")

