import uuid
import datetime
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base

def generate_uuid():
    return str(uuid.uuid4())

class Case(Base):
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    jurisdiction = Column(String(255))
    crime_type = Column(String(255))
    crime_taxonomy_code = Column(String(100))
    crime_description = Column(Text)
    defendant_age = Column(Integer)
    defendant_prior_record = Column(Boolean)
    defendant_ses = Column(String(100))
    defendant_mental_health = Column(Text)
    defendant_cooperation = Column(Boolean)
    victim_type = Column(String(100))
    harm_severity = Column(Text)
    actual_sentence_type = Column(String(100))
    actual_sentence_duration_months = Column(Float)
    actual_sentence_detail = Column(Text)
    case_context = Column(Text)
    source_url = Column(Text)
    status = Column(String(50), default='pending')
    
    analyses = relationship("Analysis", back_populates="case", cascade="all, delete")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    confidence_score = Column(Integer)
    confidence_breakdown = Column(JSON)
    layer1_result = Column(JSON)
    layer2_result = Column(JSON)
    layer3_result = Column(JSON)
    layer4_result = Column(JSON)
    layer5_result = Column(JSON)
    layer6_result = Column(JSON)
    verdict_classification = Column(String(50))
    recommended_range_min_months = Column(Float)
    recommended_range_max_months = Column(Float)
    full_reasoning_chain = Column(Text)
    summary = Column(Text)
    
    case = relationship("Case", back_populates="analyses")
    citations = relationship("Citation", back_populates="analysis", cascade="all, delete")
    challenges = relationship("Challenge", back_populates="analysis", cascade="all, delete")

class Citation(Base):
    __tablename__ = "citations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("analyses.id"))
    layer = Column(Integer)
    source_url = Column(Text)
    source_title = Column(Text)
    source_type = Column(String(100))
    access_date = Column(DateTime, default=datetime.datetime.utcnow)
    relevance_score = Column(Float)
    excerpt = Column(Text)
    
    analysis = relationship("Analysis", back_populates="citations")

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("analyses.id"))
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    layer_challenged = Column(Integer)
    challenge_text = Column(Text)
    status = Column(String(50), default='open')
    
    analysis = relationship("Analysis", back_populates="challenges")
