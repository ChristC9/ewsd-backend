from sqlalchemy import Column, Integer, Boolean, Date, UUID, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import CommonBase, generate_uuid

class Like(CommonBase):
    __tablename__ = 'tblidealikes'

    collikeid = Column(Integer, primary_key=True, autoincrement=True)
    collikeuid = Column(UUID(as_uuid=True), default=generate_uuid, unique=True, nullable=False)
    colideaid = Column(Integer, ForeignKey('tblideas.colideaid'), nullable=False)
    colisliked = Column(Boolean)
    colpostedby = Column(Integer, ForeignKey('users.id'), nullable=False)
    colpostedon = Column(Date)

    user = relationship("User", lazy="selectin")
    idea = relationship("Idea", back_populates="likes", lazy="selectin")