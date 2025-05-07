from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import DATABASE_URL

Base = declarative_base()

class Candidate(Base):
    __tablename__ = 'candidates'

    id = Column(Integer, primary_key=True)
    salesforce_id = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    name = Column(String(255))
    phone = Column(String(50))
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    email_records = relationship("EmailRecord", back_populates="candidate")

class EmailRecord(Base):
    __tablename__ = 'email_records'

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    gmail_message_id = Column(String(255), unique=True)
    subject = Column(String(255))
    sender = Column(String(255))
    category = Column(String(50))
    received_at = Column(DateTime)
    processed_at = Column(DateTime, default=datetime.utcnow)
    response_generated = Column(Text, nullable=True)
    response_sent = Column(Boolean, default=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="email_records")

class ApplicationCount(Base):
    __tablename__ = 'application_counts'

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    date = Column(DateTime)
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate")

def init_db():
    """Initialize the database and create all tables."""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Create a new database session."""
    from sqlalchemy.orm import sessionmaker
    engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session() 