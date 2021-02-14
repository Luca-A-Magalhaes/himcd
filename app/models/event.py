from app import db
from app.models import Base
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, Boolean, Text


class Event(Base):
    __tablename__ = 'event'
    place = Column(String(80), nullable=False)
    date = Column(DateTime, nullable=False)
    desc = Column(String(255), nullable=False)
    fulltext = Column(Text, nullable=False)
    highlight = Column(Integer, default=0, nullable=False)
    source = Column(String(255), nullable=False)
    is_validated = Column(Boolean, default=False)