import json
import time
from langchain_core.prompts import PromptTemplate
from backend.workflows.state import RecruiterState
from backend.agents.screening_agent import llm
from backend.utils.metrics import record_metric

def evaluation_agent_node(state: RecruiterState) -> RecruiterState:
    """Candidate Evaluation Agent: Generates weighted score and recommendation."""
    # From state
    jd_keywords = state.get("jd_keywords", [])
    candidate_skills = state.get("skills", [])
    jd_text = state.get("jd_text", "")
    experience = state.get("experience", [])
    education = state.get("education", [])
    projects = state.get("projects", [])
    notice_period = state.get("notice_period", "Not specified")
    
    # 1. Basic Compare
    jd_set = set([k.lower() for k in jd_keywords])
    cand_set = set([s.lower() for s in candidate_skills])
    
    matched = list(jd_set.intersection(cand_set))
    missing = list(jd_set.difference(cand_set))
    
    # 2. LLM Weighted Scoring
    prompt = PromptTemplate(
        input_variables=["jd", "skills", "experience", "education", "projects", "notice_period"],
        template="""Evaluate the candidate against the Job Description. 
You must score the candidate from 0 to 100 on each of the following 5 criteria based on the provided data:
1. Skills Match
2. Experience Match
3. Education Match
4. Projects/Portfolio Match
5. Notice Period Match

Job Description:
{jd}

Candidate Data:
Skills: {skills}
Experience: {experience}
Education: {education}
Projects: {projects}
Notice Period: {notice_period}

Return ONLY a valid JSON object with EXACTLY these integer keys:
"skills_score", "experience_score", "education_score", "projects_score", "notice_period_score".
If data for a category is missing but not strictly required, score it fairly (e.g. 50). Do not use markdown formatting outside the JSON block.
"""
    )
    chain = prompt | llm
    try:
        start = time.time()
        response = chain.invoke({
            "jd": jd_text,
            "skills": json.dumps(candidate_skills),
            "experience": json.dumps(experience),
            "education": json.dumps(education),
            "projects": json.dumps(projects),
            "notice_period": notice_period
        })
        record_metric("llm_response_time", time.time() - start)
        
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        scores = json.loads(content)
        s_skills = int(scores.get("skills_score", 0))
        s_exp = int(scores.get("experience_score", 0))
        s_edu = int(scores.get("education_score", 0))
        s_proj = int(scores.get("projects_score", 0))
        s_not = int(scores.get("notice_period_score", 0))
    except Exception as e:
        print(f"Error in LLM scoring: {e}")
        # Fallback
        total_overlap = len(matched) + len(missing)
        s_skills = int((len(matched) / total_overlap) * 100) if total_overlap > 0 else 0
        s_exp = 50
        s_edu = 50
        s_proj = 50
        s_not = 50
        
    # Calculate weighted total
    total_score = (s_skills * 0.50) + (s_exp * 0.20) + (s_edu * 0.15) + (s_proj * 0.10) + (s_not * 0.05)
    total_score = round(total_score, 2)
    
    # Store breakdown as JSON string
    breakdown = {
        "Skills": {"score": s_skills, "weight": "50%"},
        "Experience": {"score": s_exp, "weight": "20%"},
        "Education": {"score": s_edu, "weight": "15%"},
        "Projects": {"score": s_proj, "weight": "10%"},
        "Notice Period": {"score": s_not, "weight": "5%"}
    }
    
    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_score": total_score,
        "score_breakdown": json.dumps(breakdown)
    }
