from sqlalchemy import Column, Integer, String, ForeignKey, UUID
from app.models.base import CommonBase, generate_uuid


class Report(CommonBase):
    __tablename__ = 'tblreports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    reportguid = Column(UUID(as_uuid=True), default=generate_uuid, unique=True, nullable=False)
    ideaid = Column(Integer, ForeignKey('tblideas.id'), nullable=False)
    reportedby = Column(Integer, ForeignKey('users.id'), nullable=False)
    reportedreason = Column(String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "ideaid": self.ideaid,
            "reportedby": self.reportedby,
            "reportedreason": self.reportedreason
        }