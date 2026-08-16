import enum
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, Enum as SQLEnum, ForeignKey
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

class SourcingStage(str, enum.Enum):
    DISCOVERED = "Discovered"
    CONTACTED = "Contacted"
    INTERESTED = "Interested"
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
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

    # Diversity & Inclusion fields
    gender = Column(String, nullable=True)
    total_experience_years = Column(Float, nullable=True)
    highest_education_level = Column(String, nullable=True)

    # Relationships
    comments = relationship("Comment", back_populates="candidate", cascade="all, delete-orphan")
    journey_history = relationship("CandidateJourney", back_populates="candidate", cascade="all, delete-orphan", order_by="CandidateJourney.created_at.asc()")
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")
    assessment_results = relationship("AssessmentResult", back_populates="candidate", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="candidate", cascade="all, delete-orphan")
    onboarding_records = relationship("Onboarding", back_populates="candidate", cascade="all, delete-orphan")
    communications = relationship("CommunicationHistory", back_populates="candidate", cascade="all, delete-orphan")
    social_profiles = relationship("SocialProfile", back_populates="candidate", cascade="all, delete-orphan")
    sources = relationship("CandidateSource", back_populates="candidate", cascade="all, delete-orphan")
    pipeline_records = relationship("CandidatePipeline", back_populates="candidate", cascade="all, delete-orphan")

class CandidateJourney(Base):
    __tablename__ = "candidate_journeys"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = Column(String, nullable=False)
    status = Column(String, nullable=False)
    remarks = Column(Text, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="journey_history")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    author = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="comments")

class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_description = Column(Text, nullable=False)
    match_score = Column(Float, nullable=False)
    matched_skills = Column(Text, nullable=False)   # JSON array of strings
    missing_skills = Column(Text, nullable=False)   # JSON array of strings
    extra_skills = Column(Text, nullable=False)     # JSON array of strings
    summary = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate")

# --- Recruitment Lifecycle Models ---

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    department = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    status = Column(String, default="Active", nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    stages = relationship("RecruitmentStage", back_populates="job", cascade="all, delete-orphan", order_by="RecruitmentStage.stage_order.asc()")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

class RecruitmentStage(Base):
    __tablename__ = "recruitment_stages"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String, nullable=False)
    stage_order = Column(Integer, default=1, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("Job", back_populates="stages")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    source = Column(String, default="Direct", nullable=False)
    current_stage_id = Column(Integer, ForeignKey("recruitment_stages.id", ondelete="SET NULL"), nullable=True)
    stage_name = Column(String, default="Screening", nullable=False)
    status = Column(String, default="In Progress", nullable=False) # In Progress, Passed, Rejected, Hired
    
    applied_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    current_stage = relationship("RecruitmentStage")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")
    assessment_results = relationship("AssessmentResult", back_populates="application", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="application", cascade="all, delete-orphan")
    onboarding = relationship("Onboarding", back_populates="application", cascade="all, delete-orphan")

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    interviewer = Column(String, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    interview_type = Column(String, default="Technical", nullable=False) # Technical, HR, System Design, Cultural Fit
    status = Column(String, default="Scheduled", nullable=False) # Scheduled, Completed, Cancelled, Rescheduled
    meeting_link = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    application = relationship("Application", back_populates="interviews")
    feedbacks = relationship("InterviewFeedback", back_populates="interview", cascade="all, delete-orphan")

class InterviewFeedback(Base):
    __tablename__ = "interview_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    interviewer = Column(String, nullable=False)
    feedback = Column(Text, nullable=False)
    rating = Column(Float, nullable=False) # 1.0 - 5.0
    recommendation = Column(String, nullable=True) # Strong Hire, Hire, Neutral, No Hire

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview = relationship("Interview", back_populates="feedbacks")

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    assessment_type = Column(String, default="Technical", nullable=False) # Coding, Aptitude, Psychometric
    max_score = Column(Float, default=100.0, nullable=False)
    passing_score = Column(Float, default=60.0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=True, index=True)
    score = Column(Float, nullable=False)
    result = Column(String, default="Pass", nullable=False) # Pass, Fail, Pending
    feedback = Column(Text, nullable=True)

    taken_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    assessment = relationship("Assessment")
    candidate = relationship("Candidate", back_populates="assessment_results")
    application = relationship("Application", back_populates="assessment_results")

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=True, index=True)
    salary = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    joining_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="Draft", nullable=False) # Draft, Sent, Accepted, Rejected, Expired
    sent_date = Column(DateTime(timezone=True), nullable=True)
    accepted_rejected_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="offers")
    application = relationship("Application", back_populates="offers")

class Onboarding(Base):
    __tablename__ = "onboarding"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=True, index=True)
    joining_status = Column(String, default="Pending", nullable=False) # Pending, In Progress, Joined, No Show
    document_verification = Column(String, default="Pending", nullable=False) # Pending, Verified, Failed
    background_check_status = Column(String, default="Pending", nullable=False) # Pending, In Progress, Passed, Failed
    joining_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="onboarding_records")
    application = relationship("Application", back_populates="onboarding")

class CommunicationHistory(Base):
    __tablename__ = "communication_histories"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    communication_type = Column(String, default="Email", nullable=False) # Email, SMS, LinkedIn Message, Phone Call
    subject = Column(String, nullable=True)
    message = Column(Text, nullable=False)

    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="communications")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="SET NULL"), nullable=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    performer = Column(String, nullable=False)
    action = Column(String, nullable=False)
    details = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- Sourcing & Social Integration Models ---

class SocialProfile(Base):
    __tablename__ = "social_profiles"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String, nullable=False, index=True) # LinkedIn, GitHub, Naukri, Indeed, Twitter, Other
    profile_url = Column(String, nullable=False)
    username = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    skills = Column(Text, nullable=True) # Comma-separated or JSON list
    followers = Column(Integer, default=0, nullable=False)
    repositories_count = Column(Integer, nullable=True)
    top_languages = Column(Text, nullable=True)
    total_stars = Column(Integer, nullable=True)
    raw_data = Column(Text, nullable=True) # JSON payload

    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="social_profiles")

class CandidateSource(Base):
    __tablename__ = "candidate_sources"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    source_platform = Column(String, nullable=False, index=True) # LinkedIn, GitHub, Naukri, Indeed, Referral, Career Website, Other
    source_url = Column(String, nullable=True)
    recruiter = Column(String, nullable=True)

    discovered_date = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="sources")

class CandidatePipeline(Base):
    __tablename__ = "candidate_pipelines"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String, nullable=False)
    stage = Column(String, default="Discovered", nullable=False) # Discovered, Contacted, Interested, Applied, Interview, Offer, Hired
    recruiter = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="pipeline_records")



