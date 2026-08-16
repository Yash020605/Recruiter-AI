from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class SocialProfileBase(BaseModel):
    platform: str
    profile_url: str
    username: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[str] = None
    followers: int = 0
    repositories_count: Optional[int] = None
    top_languages: Optional[str] = None
    total_stars: Optional[int] = None
    raw_data: Optional[str] = None

class SocialProfileCreate(SocialProfileBase):
    pass

class SocialProfileUpdate(BaseModel):
    profile_url: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[str] = None
    followers: Optional[int] = None
    repositories_count: Optional[int] = None
    top_languages: Optional[str] = None
    total_stars: Optional[int] = None
    raw_data: Optional[str] = None

class SocialProfileResponse(SocialProfileBase):
    id: int
    candidate_id: int
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)

class CandidateSourceBase(BaseModel):
    source_platform: str
    source_url: Optional[str] = None
    recruiter: Optional[str] = None

class CandidateSourceCreate(CandidateSourceBase):
    pass

class CandidateSourceResponse(CandidateSourceBase):
    id: int
    candidate_id: int
    discovered_date: datetime

    model_config = ConfigDict(from_attributes=True)

class CandidatePipelineBase(BaseModel):
    source: str
    stage: str = "Discovered" # Discovered, Contacted, Interested, Applied, Interview, Offer, Hired
    recruiter: Optional[str] = None
    notes: Optional[str] = None

class CandidatePipelineCreate(CandidatePipelineBase):
    pass

class CandidatePipelineUpdate(BaseModel):
    stage: Optional[str] = None
    recruiter: Optional[str] = None
    notes: Optional[str] = None

class CandidatePipelineResponse(CandidatePipelineBase):
    id: int
    candidate_id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Sourced Candidate Creation & Response ---
class SourcedCandidateCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    current_company: Optional[str] = None
    preferred_location: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None

    # Sourcing specifics
    source_platform: str = "LinkedIn" # LinkedIn, GitHub, Naukri, Indeed, Referral, Career Website, Other
    source_url: Optional[str] = None
    recruiter: Optional[str] = None
    initial_notes: Optional[str] = None

    # Optional social profile payload (e.g. GitHub username or LinkedIn URL)
    social_profiles: Optional[List[SocialProfileCreate]] = None

class SourcedCandidateResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    current_company: Optional[str] = None
    preferred_location: Optional[str] = None
    skills: Optional[str] = None
    match_score: Optional[float] = None
    recommendation: Optional[str] = None
    created_at: datetime
    sources: List[CandidateSourceResponse] = []
    social_profiles: List[SocialProfileResponse] = []
    pipeline_records: List[CandidatePipelineResponse] = []

    model_config = ConfigDict(from_attributes=True)

class SourcedCandidateRankRequest(BaseModel):
    job_description: str
