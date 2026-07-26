import json
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

# Import existing tools/agents
from backend.tools.resume_parser import extract_text_from_file
from backend.agents.screening_agent import (
    extract_skills_node,
    extract_experience_node,
    extract_education_node,
    extract_recruitment_details_node,
    extract_projects_and_certs_node
)
from backend.agents.jd_agent import jd_agent_node
from backend.agents.evaluation_agent import evaluation_agent_node
from backend.agents.recommendation_agent import recommendation_agent_node

# Define State
class RecruitmentState(TypedDict):
    resume_path: str
    jd_text: str
    
    # State fields carrying extracted info
    resume_data: Optional[Dict[str, Any]]
    extracted_skills: Optional[List[str]]
    job_requirements: Optional[Dict[str, Any]]
    match_score: Optional[float]
    recommendation: Optional[str]
    final_report: Optional[Dict[str, Any]]

# Define Node functions
def resume_parsing_node(state: RecruitmentState) -> dict:
    """Node 1: Resume Parsing (calls existing parser to get text)."""
    try:
        raw_text = extract_text_from_file(state["resume_path"])
    except Exception as e:
        raw_text = f"Error reading file: {str(e)}"
    
    return {
        "resume_data": {
            "raw_text": raw_text
        }
    }

def resume_extraction_node(state: RecruitmentState) -> dict:
    """Node 2: Resume Information Extraction (extracts structured experience, education, details, projects/certs)."""
    resume_data = state.get("resume_data") or {}
    raw_text = resume_data.get("raw_text", "")
    temp_state = {"raw_resume_text": raw_text}
    
    exp_res = extract_experience_node(temp_state) # type: ignore
    edu_res = extract_education_node(temp_state) # type: ignore
    details_res = extract_recruitment_details_node(temp_state) # type: ignore
    proj_res = extract_projects_and_certs_node(temp_state) # type: ignore
    
    updated_resume_data = {
        "raw_text": raw_text,
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
    
    return {"resume_data": updated_resume_data}

def skill_extraction_node(state: RecruitmentState) -> dict:
    """Node 3: Skill Extraction (calls existing skills extractor on raw resume text)."""
    resume_data = state.get("resume_data") or {}
    raw_text = resume_data.get("raw_text", "")
    temp_state = {"raw_resume_text": raw_text}
    
    skills_res = extract_skills_node(temp_state) # type: ignore
    return {"extracted_skills": skills_res.get("skills", [])}

def job_requirement_extraction_node(state: RecruitmentState) -> dict:
    """Node 4: Job Requirement Extraction (uses jd_agent to extract details from JD)."""
    temp_state = {"jd_text": state["jd_text"]}
    jd_res = jd_agent_node(temp_state) # type: ignore
    
    return {
        "job_requirements": {
            "jd_keywords": jd_res.get("jd_keywords", []),
            "jd_mandatory_skills": jd_res.get("jd_mandatory_skills", []),
            "jd_preferred_skills": jd_res.get("jd_preferred_skills", []),
            "jd_experience_required": jd_res.get("jd_experience_required", ""),
            "jd_salary": jd_res.get("jd_salary", ""),
            "jd_location": jd_res.get("jd_location", ""),
            "jd_notice_period": jd_res.get("jd_notice_period", ""),
            "jd_hiring_profile": jd_res.get("jd_hiring_profile", "")
        }
    }

def resume_job_matching_node(state: RecruitmentState) -> dict:
    """Node 5: Resume vs Job Matching (compares candidate skills against job requirements)."""
    cand_skills = state.get("extracted_skills") or []
    job_reqs = state.get("job_requirements") or {}
    req_skills = job_reqs.get("jd_keywords") or []
    
    jd_set = set([k.lower() for k in req_skills])
    cand_set = set([s.lower() for s in cand_skills])
    
    matched = list(jd_set.intersection(cand_set))
    missing = list(jd_set.difference(cand_set))
    
    return {
        "final_report": {
            "matched_skills": matched,
            "missing_skills": missing
        }
    }

def candidate_scoring_node(state: RecruitmentState) -> dict:
    """Node 6: Candidate Scoring (calls evaluation agent to generate score and breakdown)."""
    resume_data = state.get("resume_data") or {}
    job_reqs = state.get("job_requirements") or {}
    
    temp_state = {
        "jd_keywords": job_reqs.get("jd_keywords", []),
        "skills": state.get("extracted_skills", []),
        "jd_text": state.get("jd_text", ""),
        "experience": resume_data.get("experience", []),
        "education": resume_data.get("education", []),
        "projects": resume_data.get("projects", []),
        "notice_period": resume_data.get("notice_period", "Not specified")
    }
    
    eval_res = evaluation_agent_node(temp_state) # type: ignore
    
    report = dict(state.get("final_report") or {})
    report.update({
        "score_breakdown": eval_res.get("score_breakdown", "{}")
    })
    
    return {
        "match_score": eval_res.get("match_score", 0.0),
        "final_report": report
    }

def ai_recommendation_node(state: RecruitmentState) -> dict:
    """Node 7: AI Recommendation (calls recommendation agent)."""
    report = state.get("final_report") or {}
    
    temp_state = {
        "match_score": state.get("match_score", 0.0),
        "score_breakdown": report.get("score_breakdown", "{}"),
        "jd_text": state.get("jd_text", "")
    }
    
    rec_res = recommendation_agent_node(temp_state) # type: ignore
    
    return {
        "recommendation": rec_res.get("recommendation", "")
    }

def automated_screening_node(state: RecruitmentState) -> dict:
    """Node 8: Automated Screening Decision."""
    score = state.get("match_score", 0.0)
    resume_data = state.get("resume_data") or {}
    
    # We can add more complex rules here based on CTC, notice period, location.
    # For now, we do a basic thresholding.
    if score >= 70.0:
        status = "Shortlisted"
    elif score >= 50.0:
        status = "Screening"
    else:
        status = "Rejected"
        
    return {
        "final_report": {
            **state.get("final_report", {}),
            "automated_decision": status
        }
    }

# Build and Compile Graph
def build_recruitment_workflow():
    workflow = StateGraph(RecruitmentState)
    
    # Add Nodes
    workflow.add_node("resume_parsing", resume_parsing_node)
    workflow.add_node("resume_extraction", resume_extraction_node)
    workflow.add_node("skill_extraction", skill_extraction_node)
    workflow.add_node("job_requirement_extraction", job_requirement_extraction_node)
    workflow.add_node("resume_job_matching", resume_job_matching_node)
    workflow.add_node("candidate_scoring", candidate_scoring_node)
    workflow.add_node("ai_recommendation", ai_recommendation_node)
    workflow.add_node("automated_screening", automated_screening_node)
    
    # Set Entry Point
    workflow.set_entry_point("resume_parsing")
    
    # Set Sequential Edges
    workflow.add_edge("resume_parsing", "resume_extraction")
    workflow.add_edge("resume_extraction", "skill_extraction")
    workflow.add_edge("skill_extraction", "job_requirement_extraction")
    workflow.add_edge("job_requirement_extraction", "resume_job_matching")
    workflow.add_edge("resume_job_matching", "candidate_scoring")
    workflow.add_edge("candidate_scoring", "ai_recommendation")
    workflow.add_edge("ai_recommendation", "automated_screening")
    workflow.add_edge("automated_screening", END)
    
    return workflow.compile()

recruitment_workflow = build_recruitment_workflow()
