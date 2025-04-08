import re
from fastapi import HTTPException, status
from typing import List, Dict, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from datetime import datetime,timezone, timedelta

from sqlmodel import distinct

from app.models.idea_model import Idea
from app.models.user_model import User
from app.models.department_model import Department
from app.models.category_model import Category
from app.models.comment_model import Comment

from app.models.pages_access_model import PagesAccess
from app.utils.helpers import compute_pagination
from app.schema.pagination import PaginationRequest


class DashboardRepository:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_ideas_count_by_department(self) -> List:
        stmt = (
            select(
                Department.name,
                func.count(Idea.id).label('count')
            )
            .join(
                User, Department.id == User.department_id
            )
            .join(
                Idea, User.id == Idea.postedby
            )
            .group_by(Department.name)
        )
        
        result = await self.db.execute(stmt)
        ideas_count_by_dep = result.unique().all()
        
        return ideas_count_by_dep


    async def get_ideas_count_by_category(self) -> List:
        stmt = (
            select(
                Category.categoryname,
                func.count(Idea.id).label('count')
            )
            .join(
                Category, Idea.categoryid == Category.categoryid
            )
            .group_by(Category.categoryname)
        )
        
        result = await self.db.execute(stmt)
        ideas_count_by_cat = result.unique().all()
        
        return ideas_count_by_cat


    async def get_contributers_count_by_department(self) -> List:
        stmt = (
            select(
                Department.name,
                func.count(distinct(User.id)).label('count')
            )
            .join(
                User, Department.id == User.department_id
            )
            .join(
                Idea, User.id == Idea.postedby
            )
            .group_by(Department.name)
        )
        
        result = await self.db.execute(stmt)
        contributers_count_by_dep = result.unique().all()
        
        return contributers_count_by_dep
    

    async def get_anonymous_stats(self):
        """
        Get the count of ideas posted by anonymous users
        Get the count of comments posted by anonymous users
        """
        anon_idea_query = (
            select(
                func.count(Idea.id)
            )
            .where(Idea.ispostedanon == True)
        )
        result = await self.db.execute(anon_idea_query)
        anon_idea_count = result.unique().scalar_one_or_none()

        anon_comment_count_query = (
            select(
                func.count(Comment.id)
            )
            .where(Comment.ispostedanon == True)
        )
        result = await self.db.execute(anon_comment_count_query)
        anon_comment_count = result.unique().scalar_one_or_none()
        
        return {
            "ideasCount": anon_idea_count,
            "commentsCount": anon_comment_count
        }
    

    async def get_most_active_users(self, 
                                    params: PaginationRequest, 
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> Tuple[List[Dict], Dict]:
        """
        Get users with the most page access activities
        """
        try:
            # Build the query to count page accesses grouped by user
            query = (
                select(
                    User,
                    func.count(PagesAccess.id).label("activity_count")
                )
                .join(PagesAccess, User.id == PagesAccess.accessedby)
                .group_by(User.id)
                .order_by(desc("activity_count"))
            )
            
            # Apply date filters if provided
            if start_date:
                query = query.where(PagesAccess.accessedon >= start_date)
            if end_date:
                query = query.where(PagesAccess.accessedon <= end_date)
                
            # Get total count for pagination
            count_query = (
                select(func.count())
                .select_from(
                    select(User.id)
                    .join(PagesAccess, User.id == PagesAccess.accessedby)
                    .group_by(User.id)
                    .subquery()
                )
            )
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar_one_or_none() or 0
            
            # Apply pagination
            offset = (params.page - 1) * params.limit
            query = query.offset(offset).limit(params.limit)
            
            # Execute the query
            result = await self.db.execute(query)
            result = result.unique().all()
            
            # Format the results
            user_activities = []
            for data in result:
                user_activities.append({
                    "user": data[0],
                    "activity_count": data[1],
                })
            
            # Compute pagination info
            pagination = compute_pagination(total, params.page, params.limit)
            
            return user_activities, pagination
            
        except Exception as e:
            print(f"Error getting most active users: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve active users data")
    
    async def get_most_used_browsers(self, 
                                    limit: int = 10,
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> Dict:
        """
        Get the most commonly used browsers
        """
        try:
            # First get total page accesses for percentage calculation
            total_query = select(func.count(PagesAccess.id))
            
            # Apply date filters if provided
            if start_date:
                total_query = total_query.where(PagesAccess.accessedon >= start_date)
            if end_date:
                total_query = total_query.where(PagesAccess.accessedon <= end_date)
                
            total_result = await self.db.execute(total_query)
            total_accesses = total_result.scalar_one_or_none() or 0
            
            if total_accesses == 0:
                return {"data": [], "total_page_accesses": 0}
                
            # Build query for browser counts
            query = (
                select(
                    PagesAccess.browsername,
                    func.count(PagesAccess.id).label("count")
                )
                .group_by(PagesAccess.browsername)
                .order_by(desc("count"))
                .limit(limit)
            )
            
            # Apply the same date filters
            if start_date:
                query = query.where(PagesAccess.accessedon >= start_date)
            if end_date:
                query = query.where(PagesAccess.accessedon <= end_date)
                
            result = await self.db.execute(query)
            browsers = result.all()
            
            # Format the results with percentages
            browser_usage = []
            for browser in browsers:
                if not browser.browsername:  # Skip empty browser names
                    continue
                    
                usage_count = browser.count
                percentage = (usage_count / total_accesses) * 100
                
                browser_usage.append({
                    "browser_name": browser.browsername,
                    "usage_count": usage_count,
                    "usage_percentage": round(percentage, 2)
                })
                
            return {
                "data": browser_usage,
                "total_page_accesses": total_accesses
            }
            
        except Exception as e:
            print(f"Error getting most used browsers: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve browser usage data")