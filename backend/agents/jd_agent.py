import json
import time
from langchain_core.prompts import PromptTemplate
from backend.workflows.state import RecruiterState
from backend.agents.screening_agent import llm
from backend.utils.metrics import record_metric

def jd_agent_node(state: RecruiterState) -> RecruiterState:
    """JD Agent: Extracts core requirements, skills, and details from the Job Description."""
    jd_text = state.get("jd_text", "")
    
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Extract recruitment details from the following Job Description.
Return ONLY a valid JSON object with the following keys:
- "mandatory_skills": array of strings (e.g. ["Python", "React"])
- "preferred_skills": array of strings
- "experience_required": string (e.g. "5+ years", "Not specified")
- "salary": string (e.g. "$100k - $120k", "Not specified")
- "location": string (e.g. "Remote", "New York, NY", "Not specified")
- "notice_period": string (e.g. "Immediate", "30 days", "Not specified")
- "hiring_profile": string (e.g. "Senior Backend Engineer", "Not specified")

Job Description:
{text}
"""
    )
    chain = prompt | llm
    
    try:
        start = time.time()
        response = chain.invoke({"text": jd_text})
        record_metric("llm_response_time", time.time() - start)
        
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("LLM returned non-JSON dictionary")
            
        m_skills = data.get("mandatory_skills", [])
        p_skills = data.get("preferred_skills", [])
        exp_req = str(data.get("experience_required", "Not specified"))
        salary = str(data.get("salary", "Not specified"))
        location = str(data.get("location", "Not specified"))
        notice = str(data.get("notice_period", "Not specified"))
        h_profile = str(data.get("hiring_profile", "Not specified"))
        
        # Combine for legacy components
        if not isinstance(m_skills, list): m_skills = []
        if not isinstance(p_skills, list): p_skills = []
        all_keywords = list(set(m_skills + p_skills))
    except Exception as e:
        print(f"Error extracting JD details: {e}")
        # Fallback to simple extraction
        from backend.tools.keyword_extractor import extract_keywords_from_text
        all_keywords = extract_keywords_from_text(jd_text)
        m_skills = all_keywords
        p_skills = []
        exp_req = "Not specified"
        salary = "Not specified"
        location = "Not specified"
        notice = "Not specified"
        h_profile = "Not specified"
        
    return {
        "jd_keywords": all_keywords,
        "jd_mandatory_skills": m_skills,
        "jd_preferred_skills": p_skills,
        "jd_experience_required": exp_req,
        "jd_salary": salary,
        "jd_location": location,
        "jd_notice_period": notice,
        "jd_hiring_profile": h_profile
    }
