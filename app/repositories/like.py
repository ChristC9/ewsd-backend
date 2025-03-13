from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
from typing import List, Optional, Dict
from app.models.like_model import Like
from app.schema.like import LikeCreate

class LikeRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_like(self, db: AsyncSession, like_data: LikeCreate, user_id: int) -> Like:
        """
        Create a new like or dislike record
        """
        # Check if user already liked/disliked this idea
        query = select(Like).where(
            Like.ideaid == like_data.ideaid,
            Like.postedby == user_id
        )
        result = await db.execute(query)
        existing_like = result.scalar_one_or_none()
        
        if existing_like:
            # Update existing record
            existing_like.isliked = like_data.isliked
            existing_like.isdisliked = like_data.isdisliked
            existing_like.postedon = date.today()
            await db.commit()
            await db.refresh(existing_like)
            return existing_like
        
        # Create new like record
        like = Like(
            ideaid=like_data.ideaid,
            isliked=like_data.isliked,
            isdisliked=like_data.isdisliked,
            postedby=user_id,
            postedon=date.today()
        )
        
        try:
            db.add(like)
            await db.commit()
            await db.refresh(like)
            return like
        except SQLAlchemyError as e:
            await db.rollback()
            raise e
    
    async def get_user_like_for_idea(self, db: AsyncSession, idea_id: int, user_id: int) -> Optional[Like]:
        """
        Get a user's like/dislike for a specific idea
        """
        query = select(Like).where(
            Like.ideaid == idea_id,
            Like.postedby == user_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_likes_by_idea(self, db: AsyncSession, idea_id: int) -> List[Like]:
        """
        Get all likes for a specific idea
        """
        query = select(Like).where(Like.ideaid == idea_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def delete_like(self, db: AsyncSession, idea_id: int, user_id: int) -> bool:
        """
        Delete or update a like (set isliked to False) for a specific idea by the authenticated user
        """
        query = select(Like).where(
            Like.ideaid == idea_id, 
            Like.postedby == user_id,
            Like.isliked == True
        )
        result = await db.execute(query)
        like = result.scalar_one_or_none()
        
        if not like:
            return False
            
        try:
            # Check if it also has a dislike
            if like.isdisliked:
                # Just remove the like flag but keep the dislike
                like.isliked = False
                await db.commit()
            else:
                # If no dislike, remove the entire record
                await db.delete(like)
                await db.commit()
            return True
        except SQLAlchemyError:
            await db.rollback()
            return False

    async def delete_dislike(self, db: AsyncSession, idea_id: int, user_id: int) -> bool:
        """
        Delete or update a dislike for a specific idea
        """
        query = select(Like).where(
            Like.ideaid == idea_id, 
            Like.postedby == user_id,
            Like.isdisliked == True
        )
        result = await db.execute(query)
        dislike = result.scalar_one_or_none()
        
        if not dislike:
            return False
            
        try:
            # Check if it also has a like
            if dislike.isliked:
                # Just remove the dislike flag but keep the like
                dislike.isdisliked = False
                await db.commit()
            else:
                # If no like, remove the entire record
                await db.delete(dislike)
                await db.commit()
            return True
        except SQLAlchemyError:
            await db.rollback()
            return False

    async def get_alllike_counts_for_idea(self, db: AsyncSession, idea_id: int) -> Dict[str, int]:
        """
        Get both like and dislike counts for an idea
        """
        likes_query = select(Like).where(
            Like.ideaid == idea_id,
            Like.isliked == True
        )
        likes_result = await db.execute(likes_query)
        likes_count = len(likes_result.scalars().all())
        
        dislikes_query = select(Like).where(
            Like.ideaid == idea_id,
            Like.isdisliked == True
        )
        dislikes_result = await db.execute(dislikes_query)
        dislikes_count = len(dislikes_result.scalars().all())
        
        return {
            "likes": likes_count,
            "dislikes": dislikes_count
        }
    
    async def get_likes_counts_for_idea(self, db: AsyncSession, idea_id: int) -> int:
        """
        Get only like count for an idea
        """
        query = select(Like).where(
            Like.ideaid == idea_id,
            Like.isliked == True
        )
        result = await db.execute(query)
        return len(result.scalars().all())
    
    async def get_dislikes_counts_for_idea(self, db: AsyncSession, idea_id: int) -> int:
        """
        Get only dislike count for an idea
        """
        query = select(Like).where(
            Like.ideaid == idea_id,
            Like.isdisliked == True
        )
        result = await db.execute(query)
        return len(result.scalars().all())