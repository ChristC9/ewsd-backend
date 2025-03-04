from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.schema.comment import CommentCreate, CommentResponse
from app.repositories.comment import CommentRepository
from app.api.deps import get_db, get_current_user
from app.models.user_model import User

router = APIRouter(
    # prefix="/comments",
    # tags=["comments"],
    # responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    comment = CommentCreate(
        ideaid=comment_data.ideaid,
        comment=comment_data.comment,
        ispostedanon=comment_data.ispostedanon
    )
    
    comment_repo = CommentRepository(db)
    

    return await comment_repo.create_comment(comment, current_user.id)


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment_repo = CommentRepository(db)
    db_comment = comment_repo.get_comment_by_id(comment_id)
    
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if the current user is the author of the comment
    if db_comment.postedby != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own comments"
        )
    
    updated_comment = await comment_repo.update_comment(comment_id, comment_text)
    return updated_comment

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment_repo = CommentRepository(db)
    db_comment = comment_repo.get_comment_by_id(comment_id)
    
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if db_comment.postedby != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments"
        )
    
    comment_repo.delete_comment(comment_id)
    return {"detail": f"Comment is {comment_id} for user {current_user.id} is deleted successfully"}