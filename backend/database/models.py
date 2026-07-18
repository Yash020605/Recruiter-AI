import enum
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.postgres import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"

class CandidateStatus(str, enum.Enum):
    NEW = "New"
    SCREENING = "Screening"
    INTERVIEW_SCHEDULED = "Interview Scheduled"
    SHORTLISTED = "Shortlisted"
    REJECTED = "Rejected"
    OFFER_SENT = "Offer Sent"
    HIRED = "Hired"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.RECRUITER, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(String, default=CandidateStatus.NEW.value, nullable=False)
    
    # Recruitment Fields
    current_company = Column(String, nullable=True)
    current_ctc = Column(String, nullable=True)
    expected_ctc = Column(String, nullable=True)
    notice_period = Column(String, nullable=True)
    preferred_location = Column(String, nullable=True)
    employment_type = Column(String, nullable=True)
    immediate_joiner = Column(String, nullable=True)
    
    skills = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    projects = Column(Text, nullable=True)
    certifications = Column(Text, nullable=True)
    
    # LangGraph Output Fields
    matched_skills = Column(Text, nullable=True)
    missing_skills = Column(Text, nullable=True)
    match_score = Column(Float, nullable=True)
    score_breakdown = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    resume_path = Column(String, nullable=True)
    
    # Integration Tracking
    zoho_candidate_id = Column(String, nullable=True)
    keka_employee_id = Column(String, nullable=True)
    hackerearth_assessment_url = Column(String, nullable=True)
    hackerearth_score = Column(Float, nullable=True)
    authbridge_bgv_status = Column(String, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    comments = relationship("Comment", back_populates="candidate", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    author = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="comments")
