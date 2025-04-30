import re
from fastapi import APIRouter, status, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from typing import Optional
from datetime import datetime, date

from app.database import get_db
from app.api.deps import CurrentUser
from app.auth.permissions import Permissions, has_permission

from app.repositories import dashboard
from app.repositories.dashboard import DashboardRepository

from app.schema.pagination import PaginationRequest
from app.schema.analytical import UsersActivityResponse, MostUsedBrowsersResponse, MostUsedPagesResponse


router = APIRouter()

@router.get("/ideas-by-department", status_code=status.HTTP_200_OK)
async def get_ideas_by_department(
    current_user: CurrentUser,
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    db: AsyncSession = Depends(get_db),
):
    dashboard_repo = DashboardRepository(db)
    result = await dashboard_repo.get_ideas_count_by_department(department_id=department_id)
    return {
        'labels': [r[0] for r in result],
        'data': [r[1] for r in result]
    }
    

@router.get("/ideas-by-category", status_code=status.HTTP_200_OK)
async def get_ideas_by_category(
    current_user: CurrentUser,
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    db: AsyncSession = Depends(get_db),
):
    dashboard_repo = DashboardRepository(db)
    result = await dashboard_repo.get_ideas_count_by_category(department_id=department_id)
    return {
        'labels': [r[0] for r in result],
        'data': [r[1] for r in result]
    }


@router.get("/contributers-by-department", status_code=status.HTTP_200_OK)
async def get_contributers_by_department(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the count of users who posted ideas by department
    """
    dashboard_repo = DashboardRepository(db)
    result = await dashboard_repo.get_contributers_count_by_department()
    return {
        'labels': [r[0] for r in result],
        'data': [r[1] for r in result]
    }


@router.get("/anon-stats", status_code=status.HTTP_200_OK)
async def get_anon_stats(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the count of anonymous ideas and comments
    """
    dashboard_repo = DashboardRepository(db)
    result = await dashboard_repo.get_anonymous_stats()
    return result


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_stats(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the count of anonymous ideas, comments and no comments ideas
    """
    dashboard_repo = DashboardRepository(db)
    result = await dashboard_repo.get_stats()
    return result


@router.get("/most-active-users", response_model=UsersActivityResponse)
async def get_most_active_users(
    page: int = Query(1, description="Page number", ge=1),
    limit: int = Query(10, description="Number of users per page", ge=1, le=100),
    start_date: Optional[date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """Get users with the most page access activities"""
    
    # Convert date parameters to datetime if provided
    start_datetime = None
    end_datetime = None
    
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
    
    analytics_repo = DashboardRepository(db)
    params = PaginationRequest(page=page, limit=limit)
    users, pagination = await analytics_repo.get_most_active_users(
        params, 
        start_date=start_datetime,
        end_date=end_datetime
    )
    
    return UsersActivityResponse(
        data=users,
        pagination=pagination
    )

@router.get("/most-used-browsers", response_model=MostUsedBrowsersResponse)
async def get_most_used_browsers(
    limit: int = Query(10, description="Number of browsers to return", ge=1, le=100),
    start_date: Optional[date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """Get the most commonly used browsers"""
    
    # Convert date parameters to datetime if provided
    start_datetime = None
    end_datetime = None
    
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
    
    analytics_repo = DashboardRepository(db)
    result = await analytics_repo.get_most_used_browsers(
        limit=limit,
        start_date=start_datetime,
        end_date=end_datetime
    )
    
    return result


@router.get("/most-active-pages", status_code=status.HTTP_200_OK, response_model=MostUsedPagesResponse)
async def get_most_active_pages(
    limit: int = Query(10, description="Number of pages to return", ge=1, le=100),
    start_date: Optional[date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """Get the most commonly used pages"""
    
    # Convert date parameters to datetime if provided
    start_datetime = None
    end_datetime = None
    
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
    
    analytics_repo = DashboardRepository(db)
    result = await analytics_repo.get_most_active_pages(
        limit=limit,
        start_date=start_datetime,
        end_date=end_datetime
    )
    
    return result