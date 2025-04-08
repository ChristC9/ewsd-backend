from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pages_access_model import PagesAccess
from app.schema.page_access import PageAccessCreate
from fastapi import HTTPException, status
import traceback

class PageAccessRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def record_page_access(self, page_access: PageAccessCreate) -> PagesAccess:
        """Record a new page access"""
        try:
            db_page_access = PagesAccess(
                pagename=page_access.pagename,
                accessedby=page_access.accessedby,
                browsername=page_access.browsername,
                created_by=str(page_access.accessedby),  # Assuming accessedby is the user ID
            )
            
            self.db.add(db_page_access)
            await self.db.commit()
            await self.db.refresh(db_page_access)
            
            return db_page_access
        except Exception:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            print(f"Error recording page access: {tb_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error recording page access"
            )