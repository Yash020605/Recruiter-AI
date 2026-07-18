import time
from backend.workflows.state import RecruiterState
from backend.tools.resume_parser import extract_text_from_file
from backend.agents.screening_agent import (
    extract_skills_node, 
    extract_experience_node, 
    extract_education_node, 
    extract_recruitment_details_node,
    extract_projects_and_certs_node
)
from backend.utils.metrics import record_metric

def resume_agent_node(state: RecruiterState) -> RecruiterState:
    """Resume Agent: Parses the resume and extracts skills, experience, and education."""
    # 1. Parse Resume
    try:
        start = time.time()
        text = extract_text_from_file(state["resume_path"])
        record_metric("parsing_time", time.time() - start)
    except Exception as e:
        text = f"Error reading file: {str(e)}"
    
    # Temporarily update state for inner extraction functions
    temp_state = {"raw_resume_text": text}
    
    # 2. Extract Data using existing LLM logic
    skills_res = extract_skills_node(temp_state) # type: ignore
    exp_res = extract_experience_node(temp_state) # type: ignore
    edu_res = extract_education_node(temp_state) # type: ignore
    details_res = extract_recruitment_details_node(temp_state) # type: ignore
    proj_res = extract_projects_and_certs_node(temp_state) # type: ignore
    
    return {
        "raw_resume_text": text,
        "skills": skills_res.get("skills", []),
        "experience": exp_res.get("experience", []),
        "education": edu_res.get("education", []),
        "projects": proj_res.get("projects", []),
        "certifications": proj_res.get("certifications", []),
        "current_company": details_res.get("current_company"),
        "current_ctc": details_res.get("current_ctc"),
        "expected_ctc": details_res.get("expected_ctc"),
        "notice_period": details_res.get("notice_period"),
        "preferred_location": details_res.get("preferred_location")
    }
