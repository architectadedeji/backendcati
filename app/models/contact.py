"""SQLAlchemy Contact model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from app.database import Base
from app.enums import ContactStatus


class Contact(Base):
    """Contact model representing a person being interviewed."""
    
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    serial_number = Column(String(255), nullable=False, unique=True, index=True)
    cuid = Column(String(255), nullable=True, unique=True, index=True)
    ticket_number = Column(String(255), nullable=True, unique=True, index=True)
    status = Column(
        Enum(ContactStatus, values_callable=lambda enum: [e.value for e in enum]),
        nullable=False, default=ContactStatus.ROUND_1, index=True
    )
    location = Column(String(255), nullable=True)
    notes = Column(String(1000), nullable=True)
    last_contact = Column(DateTime, nullable=True)
    interview_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    # Additional fields from SQLite
    batch_number = Column(String(100), nullable=True)
    batch_serial_number = Column(String(100), nullable=True)
    date_received = Column(String(100), nullable=True)
    ticket_number_nos = Column(String(100), nullable=True)
    study_arm = Column(String(500), nullable=True)
    method = Column(String(100), nullable=True)
