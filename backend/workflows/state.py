from typing import TypedDict, Optional, List, Dict, Any

class RecruiterState(TypedDict):
    resume_path: str
    jd_text: str
    jd_keywords: Optional[List[str]]
    jd_mandatory_skills: Optional[List[str]]
    jd_preferred_skills: Optional[List[str]]
    jd_experience_required: Optional[str]
    jd_salary: Optional[str]
    jd_location: Optional[str]
    jd_notice_period: Optional[str]
    jd_hiring_profile: Optional[str]
    
    # Extracted data
    raw_resume_text: Optional[str]
    skills: Optional[List[str]]
    experience: Optional[List[Dict[str, Any]]]
    education: Optional[List[Dict[str, Any]]]
    projects: Optional[List[Dict[str, Any]]]
    certifications: Optional[List[str]]
    current_company: Optional[str]
    current_ctc: Optional[str]
    expected_ctc: Optional[str]
    notice_period: Optional[str]
    preferred_location: Optional[str]
    
    # Comparison data
    matched_skills: Optional[List[str]]
    missing_skills: Optional[List[str]]
    match_score: Optional[float]
    score_breakdown: Optional[str]
    recommendation: Optional[str]
    
    # DB output
    candidate_id: Optional[int]
    
    # Chatbot
    messages: List[Any]
    chat_response: Optional[str]
