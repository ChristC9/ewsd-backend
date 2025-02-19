from app.models.base import CommonBase
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Department(CommonBase):
    __tablename__ = "departments"
    
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, unique=True, index=True)
    # users = relationship("User", backref="department")