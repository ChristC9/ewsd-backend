import re
from fastapi import HTTPException, status
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from datetime import datetime,timezone

from sqlmodel import distinct

from app.models.idea_model import Idea
from app.models.user_model import User
from app.models.department_model import Department
from app.models.category_model import Category
from app.models.comment_model import Comment


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