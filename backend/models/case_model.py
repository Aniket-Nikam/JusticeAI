from sqlalchemy import Column, Integer, Text, DateTime
from database import Base
import datetime

class CaseAnalysis(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    report = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
