from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True)
    firstname: str = Column(String(50))
    lastname: str = Column(String(50))
    email: str = Column(String(100),nullable=True)
    username: str = Column(String(50), unique=True)
    password: str = Column(String(255))
    role: str = Column(String(50))
    created_at: datetime = Column(DateTime, default=datetime.now)
    updated_at: datetime = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User {self.username}>"
