"""SQLAlchemy Interview models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Interview(Base):
    """Interview model representing a contact interview session."""
    
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    round_number = Column(Integer, default=1, index=True)
    status = Column(String(50), nullable=False, default="round_1", index=True)
    stage = Column(Integer, default=0)
    current_question_index = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    decline_reason = Column(String(500), nullable=True)
    xform_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    responses = relationship("Response", back_populates="interview", cascade="all, delete-orphan")
    interview_round = relationship(
        "InterviewRound",
        foreign_keys=[contact_id, round_number],
        primaryjoin="and_(Interview.contact_id==InterviewRound.contact_id, Interview.round_number==InterviewRound.round_number)",
        uselist=False,
        viewonly=True
    )


class InterviewRound(Base):
    """Interview round model representing a scheduled interview round."""
    
    __tablename__ = "interview_rounds"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    scheduled_at = Column(DateTime, nullable=True, index=True)
    can_start_interview = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Response(Base):
    """Response model storing answers to interview questions."""
    
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False, index=True)
    question_id = Column(Integer, nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    answer = Column(JSON, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interview = relationship("Interview", back_populates="responses")
