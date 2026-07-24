from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class CandidateBase(BaseModel):
    name: Optional[str] = Field(default=None, description="Candidate Name")
    email: Optional[str] = Field(default=None, description="Candidate Email")
    phone: Optional[str] = Field(default=None, description="Candidate Phone")
    status: Optional[str] = Field(default="New", description="Candidate Status")
    current_company: Optional[str] = Field(default=None, description="Current Company")
    current_ctc: Optional[str] = Field(default=None, description="Current CTC")
    expected_ctc: Optional[str] = Field(default=None, description="Expected CTC")
    notice_period: Optional[str] = Field(default=None, description="Notice Period")
    preferred_location: Optional[str] = Field(default=None, description="Preferred Location")
    employment_type: Optional[str] = Field(default=None, description="Employment Type")
    immediate_joiner: Optional[str] = Field(default=None, description="Immediate Joiner")
    skills: Optional[str] = Field(default=None, description="Extracted Skills (JSON string)")
    education: Optional[str] = Field(default=None, description="Education details (JSON string)")
    experience: Optional[str] = Field(default=None, description="Experience details (JSON string)")
    projects: Optional[str] = Field(default=None, description="Projects (JSON string)")
    certifications: Optional[str] = Field(default=None, description="Certifications (JSON string)")
    matched_skills: Optional[str] = Field(default=None, description="Matched skills (JSON string)")
    missing_skills: Optional[str] = Field(default=None, description="Missing skills (JSON string)")
    match_score: Optional[float] = Field(default=None, description="Score 0-100")
    score_breakdown: Optional[str] = Field(default=None, description="Score Breakdown (JSON string)")
    recommendation: Optional[str] = Field(default=None, description="AI Recommendation rationale")
    resume_path: Optional[str] = Field(default=None, description="Path to the uploaded PDF")
    
    # Integrations
    zoho_candidate_id: Optional[str] = Field(default=None, description="Zoho Recruit ID")
    keka_employee_id: Optional[str] = Field(default=None, description="Keka HRMS ID")
    hackerearth_assessment_url: Optional[str] = Field(default=None, description="HackerEarth Test URL")
    hackerearth_score: Optional[float] = Field(default=None, description="HackerEarth Technical Score")
    authbridge_bgv_status: Optional[str] = Field(default=None, description="AuthBridge BGV Status")
    
    # New Real Integrations
    linkedin_profile_url: Optional[str] = Field(default=None, description="LinkedIn Profile URL")
    google_meet_url: Optional[str] = Field(default=None, description="Google Meet URL")
    github_score: Optional[float] = Field(default=None, description="GitHub Technical Score")
    calendly_interview_time: Optional[str] = Field(default=None, description="Calendly Scheduled Time")
    google_sheets_sync_status: Optional[str] = Field(default=None, description="Google Sheets Sync Status")

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(CandidateBase):
    pass

class CandidateResponse(CandidateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    composite_score: Optional[float] = Field(default=None, description="Combined AI + Tech Score")
    rank: Optional[int] = Field(default=None, description="Rank position when sorted by composite score")

    model_config = ConfigDict(from_attributes=True)

class CommentBase(BaseModel):
    text: str = Field(..., description="Comment text")

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    candidate_id: int
    author: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
