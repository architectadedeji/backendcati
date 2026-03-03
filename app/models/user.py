from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.mysql import VARCHAR
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(VARCHAR(255), unique=True, nullable=False, index=True)
    email = Column(VARCHAR(255), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(VARCHAR(50), nullable=False, default="interviewer")  # admin, interviewer, contact
    phone = Column(VARCHAR(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, role={self.role})>"
