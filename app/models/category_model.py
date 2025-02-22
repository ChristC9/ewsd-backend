from sqlalchemy import Column, Integer, String, Date
from app.models.base import CommonBase

class Category(CommonBase):
    __tablename__ = "tblcategories"

    colcategoryid = Column(Integer, primary_key=True, autoincrement=True)
    colcategoryname = Column(String(200), nullable=True)