from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from datetime import datetime,timezone
from app.models.category_model import Category
from app.schema.category import CategoryCreate
from fastapi import HTTPException, status
from typing import List


class CategoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_category(self, category: CategoryCreate) -> Category:
        try:
            new_category = Category(
                name = category.name,
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
    
    
    async def get_all_categories(self) -> List[Category]:
        result = await self.db.execute(select(Category))
        categories = result.unique().scalars().all()
        return categories
    

    async def get_category(self, category_id: int) -> Category:
        query = select(Category).where(Category.id == category_id)
        result = await self.db.execute(query)
        category = result.unique().scalar_one_or_none()
        return category
    

    async def update_category(self, category_id: int, category_name: str) -> Category:
        query = select(Category).where(Category.id == category_id)
        result = await self.db.execute(query)
        category = result.unique().scalar_one_or_none()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        category.name = category_name
        await self.db.commit()
        await self.db.refresh(category)
        return category


    async def delete_category(self, category_id: int):
        query = delete(Category).where(Category.id == category_id)
        await self.db.execute(query)
        await self.db.commit()
        return {"detail": "Category deleted successfully"}
       
