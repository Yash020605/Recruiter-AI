from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Job & Stage Schemas ---
class RecruitmentStageBase(BaseModel):
    name: str
    stage_order: int = 1
    is_default: bool = False

class RecruitmentStageCreate(RecruitmentStageBase):
    pass

class RecruitmentStageResponse(RecruitmentStageBase):
    id: int
    job_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class JobBase(BaseModel):
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    description: str
    requirements: Optional[str] = None
    status: str = "Active"

class JobCreate(JobBase):
    stages: Optional[List[RecruitmentStageCreate]] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    status: Optional[str] = None

class JobResponse(JobBase):
    id: int
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    stages: List[RecruitmentStageResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- Application Schemas ---
class ApplicationBase(BaseModel):
    candidate_id: int
    job_id: Optional[int] = None
    source: str = "Direct"
    stage_name: str = "Screening"
    status: str = "In Progress"

class ApplicationCreate(ApplicationBase):
    current_stage_id: Optional[int] = None

class ApplicationUpdate(BaseModel):
    job_id: Optional[int] = None
    source: Optional[str] = None
    current_stage_id: Optional[int] = None
    stage_name: Optional[str] = None
    status: Optional[str] = None

class ApplicationResponse(ApplicationBase):
    id: int
    current_stage_id: Optional[int] = None
    applied_date: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# --- Interview & Feedback Schemas ---
class InterviewFeedbackBase(BaseModel):
    interviewer: str
    feedback: str
    rating: float = Field(..., ge=1.0, le=5.0)
    recommendation: Optional[str] = None

class InterviewFeedbackCreate(InterviewFeedbackBase):
    pass

class InterviewFeedbackResponse(InterviewFeedbackBase):
    id: int
    interview_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InterviewBase(BaseModel):
    candidate_id: int
    application_id: Optional[int] = None
    interviewer: str
    scheduled_at: datetime
    interview_type: str = "Technical"
    status: str = "Scheduled"
    meeting_link: Optional[str] = None

class InterviewCreate(InterviewBase):
    pass

class InterviewUpdate(BaseModel):
    interviewer: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    interview_type: Optional[str] = None
    status: Optional[str] = None
    meeting_link: Optional[str] = None

class InterviewResponse(InterviewBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    feedbacks: List[InterviewFeedbackResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- Assessment Schemas ---
class AssessmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    assessment_type: str = "Technical"
    max_score: float = 100.0
    passing_score: float = 60.0

class AssessmentCreate(AssessmentBase):
    pass

class AssessmentResponse(AssessmentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AssessmentResultBase(BaseModel):
    assessment_id: int
    candidate_id: int
    application_id: Optional[int] = None
    score: float
    result: str = "Pass"
    feedback: Optional[str] = None

class AssessmentResultCreate(AssessmentResultBase):
    pass

class AssessmentResultResponse(AssessmentResultBase):
    id: int
    taken_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Offer Schemas ---
class OfferBase(BaseModel):
    candidate_id: int
    application_id: Optional[int] = None
    salary: float
    currency: str = "USD"
    joining_date: Optional[datetime] = None
    status: str = "Draft"

class OfferCreate(OfferBase):
    pass

class OfferUpdate(BaseModel):
    salary: Optional[float] = None
    currency: Optional[str] = None
    joining_date: Optional[datetime] = None
    status: Optional[str] = None
    sent_date: Optional[datetime] = None
    accepted_rejected_date: Optional[datetime] = None

class OfferResponse(OfferBase):
    id: int
    sent_date: Optional[datetime] = None
    accepted_rejected_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# --- Onboarding Schemas ---
class OnboardingBase(BaseModel):
    candidate_id: int
    application_id: Optional[int] = None
    joining_status: str = "Pending"
    document_verification: str = "Pending"
    background_check_status: str = "Pending"
    joining_date: Optional[datetime] = None
    notes: Optional[str] = None

class OnboardingCreate(OnboardingBase):
    pass

class OnboardingUpdate(BaseModel):
    joining_status: Optional[str] = None
    document_verification: Optional[str] = None
    background_check_status: Optional[str] = None
    joining_date: Optional[datetime] = None
    notes: Optional[str] = None

class OnboardingResponse(OnboardingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# --- Communication & Activity Log Schemas ---
class CommunicationHistoryBase(BaseModel):
    candidate_id: int
    sender: str
    recipient: str
    communication_type: str = "Email"
    subject: Optional[str] = None
    message: str

class CommunicationHistoryCreate(CommunicationHistoryBase):
    pass

class CommunicationHistoryResponse(CommunicationHistoryBase):
    id: int
    sent_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ActivityLogBase(BaseModel):
    candidate_id: Optional[int] = None
    application_id: Optional[int] = None
    user_id: Optional[int] = None
    performer: str
    action: str
    details: Optional[str] = None

class ActivityLogCreate(ActivityLogBase):
    pass

class ActivityLogResponse(ActivityLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
