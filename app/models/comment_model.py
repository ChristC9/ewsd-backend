from sqlalchemy import Column, Integer, String, Date, Boolean, UUID, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import CommonBase, generate_uuid

class Comment(CommonBase):
    __tablename__ = 'tblideacomments'

    colcommentid = Column(Integer, primary_key=True, autoincrement=True)
    colcommentuid = Column(UUID(as_uuid=True), default=generate_uuid, unique=True, nullable=False)
    colideaid = Column(Integer, ForeignKey('tblideas.colideaid'), nullable=False)
    colcomment = Column(String)
    colpostedby = Column(Integer, ForeignKey('users.id'), nullable=False)
    colpostedon = Column(Date)
    colispostedanon = Column(Boolean, default=False)
    
    user = relationship("User", lazy="selectin")
    idea = relationship("Idea", back_populates="comments", lazy="selectin")


