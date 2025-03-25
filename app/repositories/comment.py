from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.comment_model import Comment
from app.schema.comment import CommentCreate

class CommentRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_comment(self, db:AsyncSession, comment: CommentCreate,user_id: int) -> Comment:
        db_comment = Comment(
            ideaid=comment.ideaid,
            comment=comment.comment,
            postedby=user_id,
            postedon=date.today(),
            ispostedanon=comment.ispostedanon
        )
        await db.add(db_comment)
        await db.commit()
        await db.refresh(db_comment)
        return db_comment

    def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        """Get a comment by ID"""
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    def get_comment_by_uid(self, comment_uid: UUID) -> Optional[Comment]:
        """Get a comment by UUID"""
        return self.db.query(Comment).filter(Comment.commentuid == comment_uid).first()

    def get_comments_by_idea_id(self, idea_id: int) -> List[Comment]:
        """Get all comments for a specific idea"""
        return self.db.query(Comment).filter(Comment.ideaid == idea_id).all()

    def get_comments_by_user_id(self, user_id: int) -> List[Comment]:
        """Get all comments by a specific user"""
        return self.db.query(Comment).filter(Comment.postedby == user_id).all()

    def update_comment(self, comment_id: int, comment_text: str) -> Optional[Comment]:
        """Update a comment's text"""
        db_comment = self.get_comment_by_id(comment_id)
        if db_comment:
            db_comment.comment = comment_text
            self.db.commit()
            self.db.refresh(db_comment)
        return db_comment

    def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment by ID"""
        db_comment = self.get_comment_by_id(comment_id)
        if db_comment:
            self.db.delete(db_comment)
            self.db.commit()
            return True
        return False