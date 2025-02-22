from sqlalchemy import Column, Integer, String, Date, Boolean, LargeBinary, UUID, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import CommonBase, generate_uuid


class Idea(CommonBase):
    __tablename__ = 'tblideas'

    colideaid = Column(Integer, primary_key=True, autoincrement=True)
    colideaguid = Column(UUID(as_uuid=True), default=generate_uuid, unique=True, nullable=False)
    coltitle = Column(String(255), nullable=False)
    coldescription = Column(String, nullable=True)
    colthumbnail = Column(String, nullable=True)  # Changed to String to store file path
    colpostedby = Column(Integer, ForeignKey('users.id'), nullable=False)
    colpostedon = Column(Date, nullable=False)
    colispostedanon = Column(Boolean, default=False, nullable=False)
    colisactived = Column(Boolean, default=True, nullable=False)
    colcategory = Column(Integer, ForeignKey('tblcategories.colcategoryid'), nullable=False)

    user = relationship("User", lazy="selectin")
    files = relationship("File", back_populates="idea", cascade="all, delete-orphan", lazy="selectin")
    comments = relationship("Comment", back_populates="idea", cascade="all, delete-orphan", lazy="selectin")
    likes = relationship("Like", back_populates="idea", cascade="all, delete-orphan", lazy="selectin")
    category = relationship("Category", lazy="selectin")