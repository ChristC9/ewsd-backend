from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from datetime import datetime,timezone
from app.models.category_model import Category
from app.schema.category import CategoryCreate, CategroyListRequest
from fastapi import HTTPException, status
from typing import List

from app.utils.helpers import compute_pagination



class CategoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_category(self, category: CategoryCreate) -> Category:
        try:
            new_category = Category(
                categoryname = category.name,
                created_by = category.created_by,
            )
            self.db.add(new_category)
            await self.db.commit()
            await self.db.refresh(new_category)
            return new_category
        except Exception as e:
            await self.db.rollback()
            print("Category Creation Error is " + str(e))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating category")
    
    
    async def get_all_categories(self, filter_params: CategroyListRequest) -> List[Category]:
        query = select(Category)
        if filter_params.search:
            query = query.where(Category.categoryname.ilike(f"%{filter_params.search}%"))
        
        offset = (filter_params.page - 1) * filter_params.limit
        query = query.offset(offset).limit(filter_params.limit)
        result = await self.db.execute(query)
        categories = result.unique().scalars().all()

        count_query = select(func.count(Category.categoryid))
        if filter_params.search:
            count_query = count_query.where(Category.categoryname.ilike(f"%{filter_params.search}%"))
        count_result = await self.db.execute(count_query)
        total = count_result.unique().scalar_one()

        pagination = compute_pagination(total, filter_params.page, filter_params.limit)

        return categories, pagination
    

    async def get_category(self, category_id: int) -> Category:
        query = select(Category).where(Category.categoryid == category_id)
        result = await self.db.execute(query)
        category = result.unique().scalar_one_or_none()
        return category
    

    async def update_category(self, category_id: int, category_name: str) -> Category:
        query = select(Category).where(Category.categoryid == category_id)
        result = await self.db.execute(query)
        category = result.unique().scalar_one_or_none()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        category.categoryname = category_name
        await self.db.commit()
        await self.db.refresh(category)
        return category


    async def delete_category(self, category_id: int):
        query = delete(Category).where(Category.categoryid == category_id)
        await self.db.execute(query)
        await self.db.commit()
        return {"detail": "Category deleted successfully"}
       
