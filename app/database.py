from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from .config import settings
from typing_extensions import Annotated


db_url = settings.db_url

engine = create_engine(db_url)

session_local = sessionmaker(autoflush=False, autocommit=False, bind=engine)
