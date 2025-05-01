from app.schema.restriction import RestrictionCreate, RestrictionResponse
from app.repositories.restrictions import RestrictionRepository
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user_model import User

router = APIRouter()

@router.post("/", response_model=RestrictionResponse, status_code=status.HTTP_201_CREATED)
async def create_restriction(
    restriction_data: RestrictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    restriction_repo = RestrictionRepository(db)
    try:
        new_restriction = await restriction_repo.create_restriction(
            restriction_data, 
            current_user
        )
        return new_restriction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create restriction: {str(e)}"
        )
@router.get("/", response_model=list[RestrictionResponse])
async def get_all_restrictions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    restriction_repo = RestrictionRepository(db)
    try:
        restrictions = await restriction_repo.get_all_restrictions()
        return restrictions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve restrictions: {str(e)}"
        )
@router.get("/{restriction_id}", response_model=RestrictionResponse)
async def get_restriction(
    restriction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    restriction_repo = RestrictionRepository(db)
    try:
        restriction = await restriction_repo.get_restriction(restriction_id)
        if not restriction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restriction not found")
        return restriction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve restriction: {str(e)}"
        )

@router.put("/{restriction_id}", response_model=RestrictionResponse)
async def update_restriction(
    restriction_id: int,
    restriction_data: RestrictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    restriction_repo = RestrictionRepository(db)
    try:
        updated_restriction = await restriction_repo.update_restriction(
            restriction_id, 
            restriction_data
        )
        if not updated_restriction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restriction not found")
        return updated_restriction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update restriction: {str(e)}"
        )