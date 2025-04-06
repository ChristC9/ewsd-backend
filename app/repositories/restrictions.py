from app.models.restriction_model import Restriction
from app.models.user_model import User
from app.schema.restriction import RestrictionCreate
from fastapi import HTTPException, status
class RestrictionRepository:

    def __init__(self, db):
        self.db = db
    

    async def create_restriction(self, restriction_data: RestrictionCreate, current_user: User) -> Restriction:
        
        if current_user.role.name != "admin":
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