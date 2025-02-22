from sqlalchemy import Column, Integer, String, Date, Boolean, UUID, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import CommonBase, generate_uuid

class Comment(CommonBase):
    __tablename__ = 'tblideacomments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    commentuid = Column(UUID(as_uuid=True), default=generate_uuid, unique=True, nullable=False)
    ideaid = Column(Integer, ForeignKey('tblideas.id'), nullable=False)
    comment = Column(String)
    postedby = Column(Integer, ForeignKey('users.id'), nullable=False)
    postedon = Column(Date)
    ispostedanon = Column(Boolean, default=False)
    
    user = relationship("User", lazy="selectin")
    idea = relationship("Idea", back_populates="comments", lazy="selectin")


