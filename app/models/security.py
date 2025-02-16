from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey

from app.models.base import CommonBase, Base
from app.models.user_model import User

class Otp(Base):

    __tablename__ = "tbluserotp"

    colotpid = Column(Integer, primary_key=True)
    coluserid = Column(Integer, nullable=False)
    colotp = Column(String(6))
    colisused = Column(Boolean, default=False)
    colexpiresat = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Otp {self.colotp}>"
