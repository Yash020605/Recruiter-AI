from pydantic import BaseModel
from typing import Optional


class InterviewCreate(BaseModel):
    candidate_id: int
    interviewer: str
    interview_date: str
    interview_time: str
    interview_mode: str
    meeting_link: Optional[str] = None

class InterviewUpdate(BaseModel):
    interviewer: Optional[str] = None
    interview_date: Optional[str] = None
    interview_time: Optional[str] = None
    interview_mode: Optional[str] = None
    meeting_link: Optional[str] = None
    status: Optional[str] = None
    
class InterviewResponse(BaseModel):
    id: int
    candidate_id: int
    interviewer: str
    interview_date: str
    interview_time: str
    interview_mode: str
    meeting_link: Optional[str]
    status: str

    class Config:
        from_attributes = True