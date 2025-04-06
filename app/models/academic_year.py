from operator import is_
from sqlalchemy import Column, Integer, String, Date, Boolean
from app.models.base import CommonBase

class AcademicYear(CommonBase):
    __tablename__ = "tblacademicyears"
   
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, nullable=False)
    is_current = Column(Boolean, default=False)
    submission_end_date= Column(Date, nullable=False)
    final_closure_date = Column(Date, nullable=False)


