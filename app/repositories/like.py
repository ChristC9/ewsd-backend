from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
from typing import List, Optional
from app.models.like_model import Like
from app.schema.like import LikeCreate

class LikeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def create_like(self, db: Session, like_data: LikeCreate, user_id: int) -> Like:
        """
        Create a new like or dislike record
        """
        # Check if user already liked/disliked this idea
        existing_like = db.query(Like).filter(
            Like.ideaid == like_data.ideaid,
            Like.postedby == user_id
        ).first()
        
        if existing_like:
            # Update existing record
            existing_like.isliked = like_data.isliked
            existing_like.isdisliked = like_data.isdisliked
            existing_like.postedon = date.today()
            db.commit()
            db.refresh(existing_like)
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
            db.commit()
            db.refresh(like)
            return like
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    async def get_likes_by_idea(self, db: AsyncSession, idea_id: int):
        query = select(Like).where(Like.ideaid == idea_id)
        result = await db.execute(query)
        result = result.scalars().all()
        return result


    def get_user_like_for_idea(self, db: Session, idea_id: int, user_id: int) -> Optional[Like]:
        """
        Get a user's like/dislike for a specific idea
        """
        return db.query(Like).filter(
            Like.ideaid == idea_id,
            Like.postedby == user_id
        ).first()
    
    
    def delete_like(self, db: Session, idea_id: int, user_id: int) -> bool:
        """
        Delete or update a like (set isliked to False) for a specific idea by the authenticated user
        """
        like = db.query(Like).filter(
            Like.ideaid == idea_id, 
            Like.postedby == user_id,
            Like.isliked == True
        ).first()
        
        if not like:
            return False
            
        try:
            # Check if it also has a dislike
            if like.isdisliked:
                # Just remove the like flag but keep the dislike
                like.isliked = False
                db.commit()
            else:
                # If no dislike, remove the entire record
                db.delete(like)
                db.commit()
            return True
        except SQLAlchemyError:
            db.rollback()
            return False

    def delete_dislike(self, db: Session, idea_id: int, user_id: int) -> bool:
        
        dislike = db.query(Like).filter(
            Like.ideaid == idea_id, 
            Like.postedby == user_id,
            Like.isdisliked == True
        ).first()
        
        if not dislike:
            return False
            
        try:
            # Check if it also has a like
            if dislike.isliked:
                # Just remove the dislike flag but keep the like
                dislike.isdisliked = False
                db.commit()
            else:
                # If no like, remove the entire record
                db.delete(dislike)
                db.commit()
            return True
        except SQLAlchemyError:
            db.rollback()
            return False

    def get_alllike_counts_for_idea(self, db: Session, idea_id: int) -> dict:
    
        likes_count = db.query(Like).filter(
            Like.ideaid == idea_id,
            Like.isliked == True
        ).count()
        
        dislikes_count = db.query(Like).filter(
            Like.ideaid == idea_id,
            Like.isdisliked == True
        ).count()
        
        return {
            "likes": likes_count,
            "dislikes": dislikes_count
        }
    
    def get_likes_counts_for_idea(self, db: Session, idea_id: int) -> int:
    
        return db.query(Like).filter(
            Like.ideaid == idea_id,
            Like.isliked == True
        ).count()
    
    def get_dislikes_counts_for_idea(self, db: Session, idea_id: int) -> int:
       
        return db.query(Like).filter(
            Like.ideaid == idea_id,
            Like.isdisliked == True
        ).count()