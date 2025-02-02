from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from app.models.base import CommonBase

class User(CommonBase):

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True)
    firstname: str = Column(String(50))
    lastname: str = Column(String(50))
    email: str = Column(String(100),nullable=True)
    username: str = Column(String(50), unique=True)
    password: str = Column(String(255))
    role: str = Column(String(50))
  

    def __repr__(self):
        return f"<User {self.username}>"
