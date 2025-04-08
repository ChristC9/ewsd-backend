from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import CurrentUser
from app.repositories.page_access import PageAccessRepository
from app.schema.page_access import PageAccessCreate, PageAccessResponse

router = APIRouter()

@router.post("/", response_model=PageAccessResponse, status_code=status.HTTP_201_CREATED)
async def record_page_access(
    current_user: CurrentUser,
    page_access: PageAccessCreate,
    db: AsyncSession = Depends(get_db),
):
    """Record a page access event"""
    page_access.accessedby = current_user.id
    page_access_repo = PageAccessRepository(db)
    return await page_access_repo.record_page_access(page_access)