from sqlalchemy import Column, Integer, String, ForeignKey, UUID, DateTime
from sqlalchemy import func
from app.models.base import CommonBase
from sqlalchemy.orm import relationship

class PagesAccess(CommonBase):
    __tablename__ = 'pages_access'
    
    id = Column(Integer, primary_key=True)
    pagename = Column(String(255))
    accessedby = Column(Integer, ForeignKey('users.id'), nullable=False)
    accessedon = Column(DateTime(timezone=True), default=func.now())  # For date UTC
    browsername = Column(String(255))
    
    # Define relationship to users table
    user = relationship("User", back_populates="pages_accesses", lazy='joined')

