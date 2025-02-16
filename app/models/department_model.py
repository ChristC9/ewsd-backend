from app.models.base import CommonBase
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.models.user_model import User

class Department(CommonBase):

    __tablename__ = 'departments'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(50), unique=True)
    created_by : User = Column(Integer, ForeignKey('users.id'))
    created_at: datetime = Column(DateTime, nullable=False)
    updated_at: datetime = Column(DateTime, nullable=False)