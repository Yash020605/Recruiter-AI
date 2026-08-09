from typing import TypedDict, Optional, List, Dict, Any


class RecruiterState(TypedDict):

    # Job Description
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

    # Extracted Resume Data
    raw_resume_text: Optional[str]

    skills: Optional[List[str]]
    experience: Optional[List[Dict[str, Any]]]
    education: Optional[List[Dict[str, Any]]]
    projects: Optional[List[Dict[str, Any]]]
    certifications: Optional[List[str]]

    # Candidate Recruitment Details
    current_company: Optional[str]

    # Original salary values
    current_ctc: Optional[str]
    expected_ctc: Optional[str]

    # Normalized salary values
    current_ctc_lpa: Optional[float]
    expected_ctc_lpa: Optional[float]

    # Original notice period
    notice_period: Optional[str]

    # Normalized notice period
    notice_period_days: Optional[int]

    # Immediate joining
    immediate_joiner: Optional[str]

    # Candidate preference
    preferred_location: Optional[str]

    # Employment type
    employment_type: Optional[str]

    # Comparison Data
    matched_skills: Optional[List[str]]
    missing_skills: Optional[List[str]]
    match_score: Optional[float]
    score_breakdown: Optional[str]
    recommendation: Optional[str]

    # Database Output
    candidate_id: Optional[int]

    # Chatbot
    messages: List[Any]
    chat_response: Optional[str]
