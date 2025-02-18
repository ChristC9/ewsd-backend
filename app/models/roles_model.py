from app.models.base import CommonBase
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.models.user_model import User
from sqlalchemy.orm import relationship

class Role(CommonBase):

    # __tablename__ = 'roles'

    # id: int = Column(Integer, primary_key=True)
    # name: str = Column(String(50), unique=True)
    # users_id = relationship("User", back_populates="role")


    __tablename__ = 'roles'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(50), unique=True)
    users = relationship("User", backref="role")