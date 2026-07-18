import json
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from backend.config.settings import settings
from backend.workflows.state import RecruiterState
from backend.utils.metrics import record_metric

primary_llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)
fallback_llm = ChatOpenAI(
    temperature=0, 
    model_name="nvidia/nemotron-3-ultra-550b-a55b", 
    api_key=settings.NVIDIA_API_KEY, 
    base_url="https://integrate.api.nvidia.com/v1"
)
llm = primary_llm.with_fallbacks([fallback_llm])

def extract_skills_node(state: RecruiterState) -> RecruiterState:
    """Extracts skills from raw resume text."""
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Extract all technical and soft skills from the following resume text.
Return ONLY a JSON array of strings.
Resume: {text}
"""
    )
    chain = prompt | llm
    start = time.time()
    response = chain.invoke({"text": state["raw_resume_text"]})
    record_metric("llm_response_time", time.time() - start)
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        skills = json.loads(content)
    except Exception:
        skills = []
        
    return {"skills": skills}

def extract_experience_node(state: RecruiterState) -> RecruiterState:
    """Extracts work experience from raw resume text."""
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Extract work experience from the following resume text.
Return ONLY a JSON array of objects, where each object has 'company', 'title', 'duration', and 'description'.
Resume: {text}
"""
    )
    chain = prompt | llm
    start = time.time()
    response = chain.invoke({"text": state["raw_resume_text"]})
    record_metric("llm_response_time", time.time() - start)
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        experience = json.loads(content)
    except Exception:
        experience = []
        
    return {"experience": experience}

def extract_education_node(state: RecruiterState) -> RecruiterState:
    """Extracts education details from raw resume text."""
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Extract education history from the following resume text.
Return ONLY a JSON array of objects, where each object has 'institution', 'degree', and 'year'.
Resume: {text}
"""
    )
    chain = prompt | llm
    start = time.time()
    response = chain.invoke({"text": state["raw_resume_text"]})
    record_metric("llm_response_time", time.time() - start)
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        education = json.loads(content)
    except Exception:
        education = []
        
    return {"education": education}

def extract_recruitment_details_node(state: RecruiterState) -> dict:
    """Extracts advanced recruitment details from raw resume text."""
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Extract the following details from the candidate's resume text.
Return ONLY a valid JSON object with the following keys, setting the value to null if not found:
- "current_company": string or null
- "current_ctc": string or null (e.g. "12 LPA", "$100k")
- "expected_ctc": string or null
- "notice_period": string or null (e.g. "30 days", "Immediate")
- "preferred_location": string or null

Resume: {text}
"""
    )
    chain = prompt | llm
    start = time.time()
    response = chain.invoke({"text": state["raw_resume_text"]})
    record_metric("llm_response_time", time.time() - start)
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError()
    except Exception as e:
        print(f"Error extracting resume details: {e}")
        data = {}
        
    return {
        "current_company": data.get("current_company"),
        "current_ctc": data.get("current_ctc"),
        "expected_ctc": data.get("expected_ctc"),
        "notice_period": data.get("notice_period"),
        "preferred_location": data.get("preferred_location")
    }

def extract_projects_and_certs_node(state: RecruiterState) -> dict:
    """Extracts projects and certifications from raw resume text."""
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Extract projects and certifications from the following resume text.
Return ONLY a valid JSON object with two keys:
- "projects": array of objects, where each object has 'title' and 'description'
- "certifications": array of strings

Resume: {text}
"""
    )
    chain = prompt | llm
    start = time.time()
    response = chain.invoke({"text": state["raw_resume_text"]})
    record_metric("llm_response_time", time.time() - start)
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError()
    except Exception as e:
        print(f"Error extracting projects/certs: {e}")
        data = {}
        
    return {
        "projects": data.get("projects", []),
        "certifications": data.get("certifications", [])
    }

