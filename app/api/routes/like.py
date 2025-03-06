from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schema.like import LikeCreate, LikeResponse
from app.repositories.like import LikeRepository
from app.api.deps import get_current_user

router = APIRouter()



@router.post("/", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
def create_like(
    like: LikeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        like_repository = LikeRepository(db)
        return like_repository.create_like(db, like, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create like: {str(e)}"
        )

@router.get("/{idea_id}", response_model=List[LikeResponse])
async def get_likes_for_idea(
    idea_id: int,
    db: Session = Depends(get_db)
):
    like_repository = LikeRepository(db)
    likes = await like_repository.get_likes_by_idea(db, idea_id)
    return likes

@router.get("/idea/{idea_id}/likes/count")
def get_like_counts_for_idea(
    idea_id: int,
    db: Session = Depends(get_db)
):
    like_repository = LikeRepository(db)
    return {"likes": like_repository.get_likes_counts_for_idea(db, idea_id)}

@router.get("/idea/{idea_id}/dislikes/count")
def get_dislike_counts_for_idea(
    idea_id: int,
    db: Session = Depends(get_db)
):
    like_repository = LikeRepository(db)
    return {"dislikes": like_repository.get_dislikes_counts_for_idea(db, idea_id)}

@router.get("/idea/{idea_id}/counts")
def get_all_counts_for_idea(
    idea_id: int,
    db: Session = Depends(get_db)
):
    like_repository = LikeRepository(db)
    likes = like_repository.get_likes_counts_for_idea(db, idea_id)
    dislikes = like_repository.get_dislikes_counts_for_idea(db, idea_id)
    return {"likes": likes, "dislikes": dislikes}

@router.get("/idea/{idea_id}/user", response_model=LikeResponse)
def get_user_like_for_idea(
    idea_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    like_repository = LikeRepository(db)
    like = like_repository.get_user_like_for_idea(db, idea_id, current_user.id)
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Like not found for idea ID {idea_id} by current user"
        )
    return like

@router.delete("/like/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_like(
    idea_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    like_repository = LikeRepository(db)
    success = like_repository.delete_like(db, idea_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Like for idea ID {idea_id} not found or you don't have permission to delete it"
        )
    return {"message": "Like deleted successfully"}

@router.delete("/dislike/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dislike(
    idea_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    like_repository = LikeRepository(db)
    success = like_repository.delete_dislike(db, idea_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Dislike for idea ID {idea_id} not found or you don't have permission to delete it"
        )
    return {"message": "Dislike deleted successfully"}