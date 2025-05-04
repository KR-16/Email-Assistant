from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Candidate(Base):
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True)
    salesforce_id = Column(String(50), unique=True)
    email = Column(String(255), unique=True)
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    email_stats = relationship("EmailStats", back_populates="candidate")
    email_responses = relationship("EmailResponse", back_populates="candidate")

class EmailStats(Base):
    __tablename__ = 'email_stats'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    date = Column(DateTime, default=datetime.utcnow)
    application_count = Column(Integer, default=0)
    interview_count = Column(Integer, default=0)
    offer_count = Column(Integer, default=0)
    rejection_count = Column(Integer, default=0)
    other_count = Column(Integer, default=0)
    
    candidate = relationship("Candidate", back_populates="email_stats")

class EmailResponse(Base):
    __tablename__ = 'email_responses'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    email_id = Column(String(255))
    category = Column(String(50))
    response_draft = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    candidate = relationship("Candidate", back_populates="email_responses")

def init_db():
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine 