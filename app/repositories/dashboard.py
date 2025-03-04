from fastapi import HTTPException, status
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from datetime import datetime,timezone

from app.models.idea_model import Idea
from app.models.user_model import User
from app.models.department_model import Department
from app.models.category_model import Category


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
