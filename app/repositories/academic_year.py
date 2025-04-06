from venv import create
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import Dict, List, Optional, Tuple, Any
from fastapi import HTTPException, status
from datetime import date, datetime, timedelta
import traceback

from app.utils.helpers import compute_pagination
from app.schema.academic_year import AcademicYearCreate, AcademicYearUpdate, AcademicYearListRequest, SubmissionStatusResponse

# Import the models
from app.models.academic_year import AcademicYear

class AcademicYearRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_academic_years(self, params: AcademicYearListRequest) -> Tuple[List[AcademicYear], Dict[str, Any]]:
        """Get all academic years with optional filtering"""
        query = select(AcademicYear)
        
        # Apply search filter if provided
        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(AcademicYear.name.ilike(search_term))
            
        # Filter by active status if requested
        if params.active_only:
            query = query.where(AcademicYear.is_active == True)
            
        # Order by start_date descending (newest first)
        query = query.order_by(AcademicYear.start_date.desc())
        
        # Get total count for pagination
        count_query = select(func.count(AcademicYear.id))
        if params.search:
            search_term = f"%{params.search}%"
            count_query = count_query.where(AcademicYear.name.ilike(search_term))
        if params.active_only:
            count_query = count_query.where(AcademicYear.is_active == True)
            
        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one_or_none() or 0
        
        # Apply pagination
        offset = (params.page - 1) * params.limit
        query = query.offset(offset).limit(params.limit)
        
        # Execute query
        result = await self.db.execute(query)
        academic_years = result.scalars().all()
        
        # Compute pagination info
        pagination = compute_pagination(total, params.page, params.limit)
        
        return academic_years, pagination

    async def get_academic_year_by_id(self, academic_year_id: int) -> Optional[AcademicYear]:
        """Get an academic year by ID"""
        query = select(AcademicYear).where(AcademicYear.id == academic_year_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_current_academic_year(self) -> Optional[AcademicYear]:
        """Get the current academic year"""
        query = select(AcademicYear).where(AcademicYear.is_current == True)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_academic_year(self, academic_year: AcademicYearCreate, username: str) -> AcademicYear:
        """Create a new academic year"""
        try:
            # If this is set as current, unset any existing current academic year
            if academic_year.is_current:
                await self._unset_current_academic_year()
                
            db_academic_year = AcademicYear(
                name=academic_year.name,
                start_date=academic_year.start_date,
                end_date=academic_year.end_date,
                is_active=academic_year.is_active,
                is_current=academic_year.is_current,
                submission_end_date=academic_year.submission_end_date,
                final_closure_date=academic_year.final_closure_date,
                created_by=username,  # Replace with actual user ID if available
            )
            
            self.db.add(db_academic_year)
            await self.db.commit()
            await self.db.refresh(db_academic_year)
            return db_academic_year
        except Exception:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)

    async def update_academic_year(self, academic_year_id: int, academic_year_data: AcademicYearUpdate) -> AcademicYear:
        """Update an academic year"""
        try:
            # Get existing academic year
            db_academic_year = await self.get_academic_year_by_id(academic_year_id)
            if not db_academic_year:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Academic year with ID {academic_year_id} not found"
                )

            # If setting this as current, unset any existing current academic year
            if academic_year_data.is_current:
                await self._unset_current_academic_year()

            # Update fields
            update_data = academic_year_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_academic_year, field, value)
            
            # Validation: ensure dates are consistent
            if hasattr(db_academic_year, 'start_date') and hasattr(db_academic_year, 'end_date'):
                if db_academic_year.end_date < db_academic_year.start_date:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="End date must be after start date"
                    )
                    
            if hasattr(db_academic_year, 'start_date') and hasattr(db_academic_year, 'submission_end_date'):
                if db_academic_year.submission_end_date < db_academic_year.start_date:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Submission end date cannot be before start date"
                    )
                    
            if hasattr(db_academic_year, 'submission_end_date') and hasattr(db_academic_year, 'final_closure_date'):
                if db_academic_year.final_closure_date < db_academic_year.submission_end_date:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Final closure date must be after submission end date"
                    )
                    
            if hasattr(db_academic_year, 'end_date') and hasattr(db_academic_year, 'final_closure_date'):
                if db_academic_year.final_closure_date > db_academic_year.end_date:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Final closure date cannot be after end date"
                    )

            await self.db.commit()
            await self.db.refresh(db_academic_year)
            return db_academic_year
        except HTTPException:
            # Re-raise HTTP exceptions as they're already formatted properly
            raise
        except Exception:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)

    async def delete_academic_year(self, academic_year_id: int) -> bool:
        """Delete an academic year"""
        try:
            db_academic_year = await self.get_academic_year_by_id(academic_year_id)
            if not db_academic_year:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Academic year with ID {academic_year_id} not found"
                )

            await self.db.delete(db_academic_year)
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            tb_str = traceback.format_exc()
            raise HTTPException(status_code=400, detail=tb_str)
            
    async def _unset_current_academic_year(self):
        """Helper method to unset any existing current academic year"""
        update_stmt = (
            update(AcademicYear)
            .where(AcademicYear.is_current == True)
            .values(is_current=False)
        )
        await self.db.execute(update_stmt)
        
    async def check_submission_status(self) -> SubmissionStatusResponse:
        """Check if idea submission is still open based on the current academic year"""
        current_year = await self.get_current_academic_year()
        today = date.today()
        
        if not current_year:
            return SubmissionStatusResponse(
                can_submit=False,
                is_final_closure=True,
                current_date=today,
                message="No active academic year found"
            )
            
        can_submit = today <= current_year.submission_end_date
        is_final_closure = today > current_year.submission_end_date and today <= current_year.final_closure_date
        
        days_left = None
        if can_submit:
            days_left = (current_year.submission_end_date - today).days
            
        message = "Idea submission is open"
        if not can_submit:
            if is_final_closure:
                message = "New idea submissions are closed, but you can still view and comment on existing ideas"
            else:
                message = "Idea submission period has ended"
        
        return SubmissionStatusResponse(
            can_submit=can_submit,
            is_final_closure=is_final_closure,
            current_date=today,
            submission_end_date=current_year.submission_end_date,
            final_closure_date=current_year.final_closure_date,
            days_left_for_submission=days_left,
            message=message
        )