from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError

import bcrypt
import traceback

from datetime import datetime, timezone

from app.schema.security import OtpCreate, OtpUpdate
from app.models.security import Otp


async def get_otp(db: AsyncSession, user_id: int, is_used: bool = False) -> Otp:
    query = select(Otp).where(
        and_(
            Otp.user_id == user_id,
            Otp.is_used == is_used,
            Otp.expires_at > datetime.now(timezone.utc)
        ))
    result = await db.execute(query)
    otp = result.unique().scalar_one_or_none()
    return otp


async def create_otp(db: AsyncSession, otp: OtpCreate) -> Otp:
    try:
        otp = Otp(
            user_id=otp.user_id,
            otp=otp.otp,
            expires_at=otp.expires_at,
            is_used=False,
            created_by="",
        )
        db.add(otp)
        await db.commit()
        await db.refresh(otp)
        
        return otp
    
    except Exception as e:
        await db.rollback()
        tb_str = traceback.format_exc()
        raise HTTPException(status_code=400, detail="DB error occurred")
    

async def update_otp_by_model(db: AsyncSession, otpUpdate: OtpUpdate, otp_model: Otp) -> Otp:
    try:
        otp_model.is_used = otpUpdate.is_used if otpUpdate.is_used else otp_model.is_used
        otp_model.expires_at = otpUpdate.expires_at if otpUpdate.expires_at else otp_model.expires_at
        otp_model.otp = otpUpdate.otp if otpUpdate.otp else otp_model.otp
        db.add(otp_model)
        await db.commit()
        await db.refresh(otp_model)
        
        return otp_model
    except Exception as e:
        await db.rollback()
        tb_str = traceback.format_exc()
        raise HTTPException(status_code=400, detail="DB error occurred")
        