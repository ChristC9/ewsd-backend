from datetime import datetime,timezone
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.models.base import CommonBase


class User(CommonBase):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    email = Column(String(100), nullable=True)
    username = Column(String(50), unique=True)
    default_pwd = Column(String(255))
    password = Column(String(255))
    isdisabled = Column(Boolean, default=False)
    islocked = Column(Boolean, default=False)
    lastlogin = Column(DateTime, nullable=True, default=datetime.now(timezone.utc))
    role_id = Column(Integer, ForeignKey('roles.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))


    role = relationship("Role", lazy="selectin")
    department = relationship("Department", lazy="selectin")

