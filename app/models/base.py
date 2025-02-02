import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func, text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declared_attr

from datetime import datetime, timezone

from app.database import engine


class Base(AsyncAttrs, DeclarativeBase):
    metadata = sa.MetaData()


class CommonBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=cls.get_current_timestamp_default(),
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=cls.get_current_timestamp_default(),
            onupdate=func.now(),
        )
    
    created_by = Column(String(50), nullable=True)
    updated_by = Column(String(50), nullable=True)

    @staticmethod
    def get_current_timestamp_default():
        if engine.dialect.name == "postgresql":
            return func.now()
        elif engine.dialect.name == "mssql":
            return text("GETUTCDATE()")
        elif engine.dialect.name == "sqlite":
            return text("(DATETIME('now'))")
        else:
            raise NotImplementedError(f"Unsupported dialect: {engine.dialect.name}")