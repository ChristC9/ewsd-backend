from sqlalchemy import Column, Integer, String, Date, Boolean, LargeBinary, UUID, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import CommonBase, generate_uuid


class Idea(CommonBase):
    __tablename__ = 'tblideas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ideaguid = Column(UUID(as_uuid=True), default=generate_uuid, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    thumbnail = Column(LargeBinary, nullable=True)  # Changed to String to store file path
    postedby = Column(Integer, ForeignKey('users.id'), nullable=False)
    postedon = Column(Date, nullable=False)
    ispostedanon = Column(Boolean, default=False, nullable=False)
    isactived = Column(Boolean, default=True, nullable=False)
    isreported = Column(Boolean, default=False)
    categoryid = Column(Integer, ForeignKey('tblcategories.categoryid'), nullable=False)

    user = relationship("User", lazy="selectin")
    files = relationship("File", back_populates="idea", cascade="all, delete-orphan", lazy="selectin")
    comments = relationship("Comment", back_populates="idea", cascade="all, delete-orphan", lazy="selectin")
    likes = relationship("Like", back_populates="idea", cascade="all, delete-orphan", lazy="selectin")
    category = relationship("Category", lazy="selectin")
    reports = relationship("Report", lazy="selectin")
