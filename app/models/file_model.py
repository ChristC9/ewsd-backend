from sqlalchemy import Column, Integer, String, Date, UUID, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import CommonBase, generate_uuid

class File(CommonBase):
    __tablename__ = 'tblfiles'

    colfileid = Column(Integer, primary_key=True, autoincrement=True)
    colfileguid = Column(UUID(as_uuid=True), default=generate_uuid, unique=True, nullable=False)
    colideaid = Column(Integer, ForeignKey('tblideas.colideaid'), nullable=False)
    colfilename = Column(String(255))
    colfilelocation = Column(String(500))
    colfiletype = Column(String(10))
    
    idea = relationship("Idea", back_populates="files")
