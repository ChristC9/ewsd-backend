from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import CommonBase
from sqlalchemy.sql import func


class Restriction(CommonBase):

    __tablename__ = 'restrictions'

    id = Column(Integer, primary_key=True)
    submission_date = Column(DateTime(timezone=False))
    final_closure_date = Column(DateTime(timezone=False))
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", lazy="selectin")    

