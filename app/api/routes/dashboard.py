from fastapi import APIRouter,status,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.database import get_db
from app.api.deps import CurrentUser
from app.auth.permissions import Permissions, has_permission

from app.repositories import dashboard
from app.repositories.dashboard import DashboardRepository

router = APIRouter()

@router.get("/ideas-by-department", status_code=status.HTTP_200_OK)
async def get_ideas_by_department(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    dashboard_repo = DashboardRepository(db)
    result = await dashboard_repo.get_ideas_count_by_department()
    return {
        'labels': [r[0] for r in result],
        'data': [r[1] for r in result]
    }
    

@router.get("/ideas-by-category", status_code=status.HTTP_200_OK)
async def get_ideas_by_category(
    db: AsyncSession = Depends(get_db),
):
    dashboard_repo = DashboardRepository(db)
    result = await dashboard_repo.get_ideas_count_by_category()
    return {
        'labels': [r[0] for r in result],
        'data': [r[1] for r in result]
    }