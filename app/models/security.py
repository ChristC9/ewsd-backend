from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey

from app.api.routes import user_management
from app.models.base import CommonBase
from app.models.user_model import User

class Otp(CommonBase):

    __tablename__ = "otp"

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, nullable=False)
    otp: str = Column(String(6))
    is_used: bool = Column(Boolean, default=False)
    expires_at: datetime = Column(DateTime)

    def __repr__(self):
        return f"<Otp {self.otp}>"
