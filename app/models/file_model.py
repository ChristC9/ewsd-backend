from sqlalchemy import Column, Integer, String, Date, UUID, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import CommonBase, generate_uuid

class File(CommonBase):
    __tablename__ = 'tblfiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fileguid = Column(UUID(as_uuid=True), default=generate_uuid, unique=True, nullable=False)
    ideaid = Column(Integer, ForeignKey('tblideas.id'), nullable=False)
    filename = Column(String(255))
    filelocation = Column(String(500))
    filetype = Column(String(100))
    
    idea = relationship("Idea", back_populates="files")
