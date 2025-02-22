from sqlalchemy import Column, Integer, Boolean, Date, UUID, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import CommonBase, generate_uuid

class Like(CommonBase):
    __tablename__ = 'tblidealikes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    likeuid = Column(UUID(as_uuid=True), default=generate_uuid, unique=True, nullable=False)
    ideaid = Column(Integer, ForeignKey('tblideas.id'), nullable=False)
    isliked = Column(Boolean)
    postedby = Column(Integer, ForeignKey('users.id'), nullable=False)
    postedon = Column(Date)

    user = relationship("User", lazy="selectin")
    idea = relationship("Idea", back_populates="likes", lazy="selectin")