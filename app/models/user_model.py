from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import CommonBase

# class User(CommonBase):

    # __tablename__ = "users"

    # id = Column(Integer, primary_key=True)
    # firstname = Column(String(50))
    # lastname = Column(String(50))
    # email = Column(String(100), nullable=True)
    # username = Column(String(50), unique=True)
    # default_pwd = Column(String(255))
    # password = Column(String(255))
    # role_id = Column(Integer, ForeignKey('roles.id'))
    # department_id = Column(Integer, ForeignKey('departments.id'), unique=True)
    # role = relationship("Role", back_populates="users_id")
    # departments = relationship("Department", foreign_keys=[Department.users_id], back_populates="user")
    # created_departments = relationship("Department", foreign_keys=[Department.created_by_id], back_populates="creator")


class User(CommonBase):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    email = Column(String(100), nullable=True)
    username = Column(String(50), unique=True)
    default_pwd = Column(String(255))
    password = Column(String(255))
    role_id = Column(Integer, ForeignKey('roles.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))


    role = relationship("Role", lazy="selectin")
    department = relationship("Department", lazy="selectin")