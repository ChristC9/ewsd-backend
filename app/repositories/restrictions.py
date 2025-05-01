from app.models.restriction_model import Restriction
from app.models.user_model import User
from app.schema.restriction import RestrictionCreate
from fastapi import HTTPException, status
from sqlalchemy import select
class RestrictionRepository:

    def __init__(self, db):
        self.db = db
    

    async def create_restriction(self, restriction_data: RestrictionCreate, current_user: User) -> Restriction:
        
        if current_user.role.name != "admin".upper():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can create restrictions")
        
        restriction = Restriction(
            submission_date=restriction_data.submission_date,
            final_closure_date=restriction_data.final_closure_date,
            user_id=current_user.id
        )

        try:
            self.db.add(restriction)
            await self.db.commit()
            await self.db.refresh(restriction)
            return restriction
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def get_all_restrictions(self) -> list[Restriction]:
        restrictions = await self.db.execute(
            select(Restriction)
        )
        return restrictions.scalars().all()
    
    async def get_restriction(self, restriction_id: int) -> Restriction:
        restriction = await self.db.execute(
            select(Restriction).where(Restriction.id == restriction_id)
        )
        return restriction.scalar_one_or_none()
    
    async def update_restriction(self, restriction_id: int, restriction_data: RestrictionCreate) -> Restriction:
        restriction = await self.get_restriction(restriction_id)
        if not restriction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restriction not found")
        
        restriction.submission_date = restriction_data.submission_date
        restriction.final_closure_date = restriction_data.final_closure_date

        try:
            self.db.add(restriction)
            await self.db.commit()
            await self.db.refresh(restriction)
            return restriction
        except Exception as e:
            self.db.rollback()
            raise e