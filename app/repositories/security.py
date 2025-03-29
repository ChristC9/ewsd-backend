from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import traceback

from datetime import datetime, timezone

from app.schema.security import OtpCreate, OtpUpdate
from app.models.security import Otp


async def get_otp(db: AsyncSession, user_id: int, is_used: bool = False) -> Otp:
    query = select(Otp).where(
        and_(
            Otp.coluserid == user_id,
            Otp.colisused == is_used,
            Otp.colexpiresat > datetime.now(timezone.utc)
        ))
    result = await db.execute(query)
    otp = result.unique().scalar_one_or_none()
    return otp


async def create_otp(db: AsyncSession, otp: OtpCreate) -> Otp:
    try:
        otp = Otp(
            coluserid=otp.user_id,
            colotp=otp.otp,
            colexpiresat=otp.expires_at,
            colisused=False,
        )
        db.add(otp)
        await db.commit()
        
        return otp
    
    except Exception:
        await db.rollback()
        tb_str = traceback.format_exc()
        raise HTTPException(status_code=400, detail=tb_str)
    

async def update_otp_by_model(db: AsyncSession, otp_update: OtpUpdate, otp_model: Otp) -> Otp:
    try:
        otp_model.colisused = otp_update.is_used if otp_update.is_used else otp_model.colisused
        otp_model.colexpiresat = otp_update.expires_at if otp_update.expires_at else otp_model.colexpiresat
        otp_model.colotp = otp_update.otp if otp_update.otp else otp_model.colotp
        await db.commit()

    except Exception:
        await db.rollback()
        tb_str = traceback.format_exc()
        print(tb_str)
        raise HTTPException(status_code=400, detail=tb_str)
        