from sqlalchemy import Column, Integer, String, Date
from app.models.base import CommonBase

class Category(CommonBase):
    __tablename__ = "tblcategories"

    categoryid = Column(Integer, primary_key=True, autoincrement=True)
    categoryname = Column(String(200), nullable=True)