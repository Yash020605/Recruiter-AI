import os
import uuid
import json
import asyncio
import random
import httpx
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt

from backend.config.settings import settings
from backend.database.postgres import get_db
from backend.tools.candidate_database import user_repo, candidate_repo, comment_repo
from backend.schemas.auth import Token
from backend.database.models import UserRole, Candidate, Comment, JobMatch, Interview
from backend.schemas.candidate import CandidateResponse, CommentCreate, CommentResponse
from backend.schemas.admin import UserCreate, UserUpdate, UserResponse
from backend.schemas.interview import (
    InterviewCreate,
    InterviewResponse,
    InterviewUpdate
)
from backend.utils.logger import get_logger, LOG_FILE
from backend.utils.logger import get_logger
from backend.utils.exceptions import InvalidDocumentError
from backend.agents.chatbot_agent import query_global_candidates, query_candidate
from backend.workflows.recruiter_graph import recruiter_graph
from backend.api.deps import RoleChecker
from backend.utils.metrics import get_average_metric, get_counter
from backend.ml.candidate_matcher import calculate_match_score
from backend.utils.extract_text import extract_text_from_file

logger = get_logger(__name__)
router = APIRouter()

# --- Auth Service ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- Auth Endpoints ---
@router.post("/login", response_model=Token, tags=["auth"])
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    logger.info(f"Login attempt for user: {form_data.username}")
    user = user_repo.get_by_username(db, username=form_data.username)
    
    if not user:
        mock_roles = {
            "admin": UserRole.ADMIN,
            "recruiter": UserRole.RECRUITER,
            "hiring_manager": UserRole.HIRING_MANAGER
        }
        if form_data.username in mock_roles and form_data.password == form_data.username:
            role = mock_roles[form_data.username].value
            logger.info(f"Fallback {form_data.username} login successful with role {role}.")
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": form_data.username, "role": role}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer", "role": role}
        
        logger.warning(f"Login failed: User {form_data.username} not found.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value}

# --- Upload Endpoints ---
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED, tags=["upload"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise InvalidDocumentError("Empty filename provided.")
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".txt",".docx"]:
        raise InvalidDocumentError("Only PDF, DOCX and TXT files are supported.")
        
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        content = await file.read()
        if len(content) == 0:
            raise InvalidDocumentError("The uploaded file is empty.")
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")
        
    try:
        new_candidate = candidate_repo.create(db, obj_in={
            "resume_path": file_path,
            "name": "Pending Extraction"
        })
        return new_candidate
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database operation failed.")

# --- Candidate Endpoints ---
@router.get("/candidates", response_model=List[CandidateResponse], tags=["candidates"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))])
def get_all_candidates(
    skip: int = 0, 
    limit: int = 100, 
    status_filter: Optional[str] = None,
    recommendation_filter: Optional[str] = None,
    search: Optional[str] = None,
    min_score: Optional[float] = None,
    skills: Optional[str] = None,
    notice_period: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(Candidate)
    if status_filter:
        query = query.filter(Candidate.status == status_filter)
    if recommendation_filter:
        query = query.filter(Candidate.recommendation.ilike(f"{recommendation_filter}%"))
    if search:
        query = query.filter(Candidate.name.ilike(f"%{search}%"))
    if min_score is not None:
        query = query.filter(Candidate.match_score >= min_score)
    if skills:
        query = query.filter(Candidate.skills.ilike(f"%{skills}%") | Candidate.matched_skills.ilike(f"%{skills}%"))
    if notice_period:
        query = query.filter(Candidate.notice_period.ilike(f"%{notice_period}%"))
        
    candidates_db = query.all()
    
    for c in candidates_db:
        m_score = getattr(c, 'match_score', None) or 0.0
        h_score = getattr(c, 'hackerearth_score', None)
        if h_score is not None:
            c.composite_score = (m_score * 0.6) + (h_score * 0.4)
        else:
            c.composite_score = m_score
            
    # Calculate rank based on highest composite_score
    candidates_db.sort(key=lambda x: getattr(x, 'composite_score', 0.0), reverse=True)
    for idx, c in enumerate(candidates_db):
        c.rank = idx + 1
        
    if sort_by == "match_score":
        candidates_db.sort(key=lambda x: getattr(x, 'match_score', 0.0) or 0.0, reverse=(sort_order != "asc"))
    elif sort_by == "rank":
        # default for rank is desc (highest score first). So asc means lowest score first.
        if sort_order == "asc":
            candidates_db.reverse()
    else:
        candidates_db.sort(key=lambda x: getattr(x, 'id', 0), reverse=True)
        
    return candidates_db[skip : skip + limit]

@router.get("/candidates/{candidate_id}", response_model=CandidateResponse, tags=["candidates"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))])
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return candidate

from backend.schemas.candidate import CandidateUpdate

@router.put("/candidates/{candidate_id}", response_model=CandidateResponse, tags=["candidates"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
def update_candidate(candidate_id: int, request: CandidateUpdate, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    update_data = request.model_dump(exclude_unset=True)
    updated = candidate_repo.update(db, db_obj=candidate, obj_in=update_data)
    return updated

@router.delete("/candidates/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["candidates"], dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    candidate_repo.delete(db, id=candidate_id)
    return None

# --- Comments Endpoints ---
@router.post("/candidates/{candidate_id}/comments", response_model=CommentResponse, tags=["comments"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))])
def add_comment(candidate_id: int, request: CommentCreate, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    # For now, just use a generic author string until we pull user from token properly
    # In a real app we'd decode the JWT to get the user name
    new_comment = comment_repo.create(db, obj_in={
        "candidate_id": candidate_id,
        "author": "User", 
        "text": request.text
    })
    return new_comment

@router.get("/candidates/{candidate_id}/comments", response_model=List[CommentResponse], tags=["comments"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))])
def get_comments(candidate_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.candidate_id == candidate_id).order_by(Comment.created_at.desc()).all()
    return comments

# --- Approval Endpoint ---
@router.post("/candidates/{candidate_id}/approve", response_model=CandidateResponse, tags=["candidates"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.HIRING_MANAGER]))])
def approve_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    
    updated = candidate_repo.update(db, db_obj=candidate, obj_in={
        "status": "Hired"
    })
    return updated

# --- Analyze Endpoints ---
class AnalyzeRequest(BaseModel):
    candidate_id: int
    job_description: str

class AnalyzeResponse(BaseModel):
    status: str
    message: str
    
def run_analysis_pipeline(candidate_id: int, resume_path: str, jd: str):
    logger.info(f"Starting LangGraph pipeline for candidate {candidate_id}")

    initial_state = {
        "candidate_id": candidate_id,
        "resume_path": resume_path,
        "jd_text": jd,
        "raw_resume_text": None,
        "skills": None,
        "experience": None,
        "education": None,
        "matched_skills": None,
        "missing_skills": None,
        "match_score": None,
        "recommendation": None,
        "messages": [],
        "chat_response": None
    }

    try:
        # ---------- ML Candidate Matching ----------
        resume_text = extract_text_from_file(resume_path)
        ml_match_score = calculate_match_score(jd, resume_text)
        logger.info(f"ML Candidate Match Score: {ml_match_score}%")
        # -------------------------------------------

        final_state = recruiter_graph.invoke(initial_state)

        logger.info(f"Pipeline completed with score: {final_state.get('match_score')}")

        # Save the evaluation results to the database
        try:
            db = next(get_db())
            candidate = candidate_repo.get(db, id=candidate_id)

            if candidate:
                candidate_repo.update(
                    db,
                    db_obj=candidate,
                    obj_in={
                        "skills": json.dumps(final_state.get("skills", [])),
                        "experience": json.dumps(final_state.get("experience", [])),
                        "education": json.dumps(final_state.get("education", [])),
                        "projects": json.dumps(final_state.get("projects", [])),
                        "certifications": json.dumps(final_state.get("certifications", [])),
                        "matched_skills": json.dumps(final_state.get("matched_skills", [])),
                        "missing_skills": json.dumps(final_state.get("missing_skills", [])),
                        "match_score": final_state.get("match_score", 0.0),
                        "recommendation": final_state.get("recommendation", ""),
                        "current_company": final_state.get("current_company"),
                        "current_ctc": final_state.get("current_ctc"),
                        "expected_ctc": final_state.get("expected_ctc"),
                        "notice_period": final_state.get("notice_period"),
                        "preferred_location": final_state.get("preferred_location")
                    }
                )

        except Exception as db_err:
            logger.error(f"Failed to save final state to DB: {db_err}")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Pipeline execution failed: {error_msg}")

        try:
            db = next(get_db())
            candidate = candidate_repo.get(db, id=candidate_id)

            if candidate:
                candidate_repo.update(
                    db,
                    db_obj=candidate,
                    obj_in={
                        "match_score": 0,
                        "recommendation": f"AI Analysis Failed: {error_msg}"
                    }
                )

        except Exception as db_err:
            logger.error(f"Failed to save error state to DB: {db_err}")

@router.post("/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_202_ACCEPTED, tags=["analyze"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def analyze_candidate(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    if not request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
        
    candidate = candidate_repo.get(db, id=request.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
        
    if not candidate.resume_path:
        raise HTTPException(status_code=400, detail="Candidate has no resume attached.")
        
    background_tasks.add_task(
        run_analysis_pipeline, 
        candidate_id=request.candidate_id, 
        resume_path=candidate.resume_path, 
        jd=request.job_description
    )
    
    return AnalyzeResponse(
        status="processing",
        message="Candidate analysis has been queued and is running in the background."
    )

# --- Job Match Endpoints ---
class JobMatchRequest(BaseModel):
    candidate_id: int
    job_description: str

class JobMatchResponse(BaseModel):
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]
    summary: str

@router.post("/job/match", response_model=JobMatchResponse, tags=["job"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))])
def match_job_description(
    request: JobMatchRequest,
    db: Session = Depends(get_db)
):
    if not request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
        
    candidate = candidate_repo.get(db, id=request.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
        
    # If candidate doesn't have parsed resume data, parse it on the fly
    if (not candidate.skills or not candidate.experience) and candidate.resume_path:
        from backend.agents.resume_agent import resume_agent_node
        try:
            parsed_data = resume_agent_node({"resume_path": candidate.resume_path})
            candidate = candidate_repo.update(db, db_obj=candidate, obj_in={
                "skills": json.dumps(parsed_data.get("skills", [])),
                "experience": json.dumps(parsed_data.get("experience", [])),
                "education": json.dumps(parsed_data.get("education", [])),
                "projects": json.dumps(parsed_data.get("projects", [])),
                "certifications": json.dumps(parsed_data.get("certifications", [])),
                "current_company": parsed_data.get("current_company"),
                "current_ctc": parsed_data.get("current_ctc"),
                "expected_ctc": parsed_data.get("expected_ctc"),
                "notice_period": parsed_data.get("notice_period"),
                "preferred_location": parsed_data.get("preferred_location")
            })
        except Exception as parse_err:
            logger.error(f"Error parsing resume on-the-fly for match: {parse_err}")
            
    if not candidate.skills:
        raise HTTPException(status_code=400, detail="Candidate has no parsed resume data and resume could not be parsed.")

    # 1. Extract requirements from JD using existing AI/LLM
    from backend.agents.screening_agent import llm
    from langchain_core.prompts import PromptTemplate

    jd_prompt = PromptTemplate(
        input_variables=["jd"],
        template="""Extract key job requirements from the following Job Description.
Return ONLY a valid JSON object with the following keys:
- "technical_skills": array of strings (e.g., ["Python", "Docker"])
- "soft_skills": array of strings (e.g., ["Communication", "Leadership"])
- "experience": string describing experience required
- "education": string describing education required
- "certifications": array of strings of required/preferred certifications (or empty array)

Job Description:
{jd}

Do not include any formatting other than the JSON block.
"""
    )
    
    try:
        jd_chain = jd_prompt | llm
        jd_res = jd_chain.invoke({"jd": request.job_description})
        content = jd_res.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
        jd_data = json.loads(content)
    except Exception as e:
        logger.error(f"Failed to extract JD requirements: {e}")
        jd_data = {
            "technical_skills": [],
            "soft_skills": [],
            "experience": "Not specified",
            "education": "Not specified",
            "certifications": []
        }

    # 2. Compare extracted requirements with parsed candidate data
    try:
        candidate_skills = json.loads(candidate.skills) if candidate.skills else []
    except Exception:
        candidate_skills = []
    try:
        candidate_experience = json.loads(candidate.experience) if candidate.experience else []
    except Exception:
        candidate_experience = []
    try:
        candidate_education = json.loads(candidate.education) if candidate.education else []
    except Exception:
        candidate_education = []
    try:
        candidate_projects = json.loads(candidate.projects) if candidate.projects else []
    except Exception:
        candidate_projects = []
    try:
        candidate_certifications = json.loads(candidate.certifications) if candidate.certifications else []
    except Exception:
        candidate_certifications = []

    match_prompt = PromptTemplate(
        input_variables=["jd_requirements", "candidate_skills", "candidate_experience", "candidate_education", "candidate_projects", "candidate_certifications"],
        template="""You are an expert recruiter matching a candidate's resume details against a Job Description's extracted requirements.

Extracted Job Requirements:
{jd_requirements}

Candidate Resume Details:
- Skills (Technical & Soft): {candidate_skills}
- Experience: {candidate_experience}
- Education: {candidate_education}
- Projects: {candidate_projects}
- Certifications: {candidate_certifications}

Please analyze the candidate against the requirements and provide the following:
1. "matched_skills": A list of skills/keywords from the job description that the candidate HAS.
2. "missing_skills": A list of skills/keywords from the job description that the candidate DOES NOT have.
3. "extra_skills": A list of skills/certifications the candidate has that are NOT in the job description but are valuable.
4. "match_score": An overall match percentage (0 to 100) based on how well the candidate's skills, experience, education, and certifications align with the job description.
5. "summary": A short AI summary (2-3 sentences) explaining why the candidate is or is not a good match.

Return ONLY a valid JSON object with the keys: "match_score" (number), "matched_skills" (array of strings), "missing_skills" (array of strings), "extra_skills" (array of strings), and "summary" (string).
Do not include any formatting other than the JSON block.
"""
    )

    try:
        match_chain = match_prompt | llm
        match_res = match_chain.invoke({
            "jd_requirements": json.dumps(jd_data),
            "candidate_skills": json.dumps(candidate_skills),
            "candidate_experience": json.dumps(candidate_experience),
            "candidate_education": json.dumps(candidate_education),
            "candidate_projects": json.dumps(candidate_projects),
            "candidate_certifications": json.dumps(candidate_certifications)
        })
        content = match_res.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
        result = json.loads(content)
    except Exception as e:
        logger.error(f"Failed to match candidate against JD: {e}")
        # Simple fallback
        jd_skills_set = set(jd_data.get("technical_skills", []) + jd_data.get("soft_skills", []))
        cand_skills_set = set(candidate_skills)
        matched = list(jd_skills_set.intersection(cand_skills_set))
        missing = list(jd_skills_set.difference(cand_skills_set))
        extra = list(cand_skills_set.difference(jd_skills_set))
        total_skills = len(jd_skills_set)
        score = (len(matched) / total_skills * 100) if total_skills > 0 else 50
        result = {
            "match_score": round(score, 2),
            "matched_skills": matched,
            "missing_skills": missing,
            "extra_skills": extra,
            "summary": "Match computed using fallback keyword overlap logic due to LLM match error."
        }

    # Save the match details to the database for analytics
    new_match = JobMatch(
        candidate_id=request.candidate_id,
        job_description=request.job_description,
        match_score=float(result.get("match_score", 0.0)),
        matched_skills=json.dumps(result.get("matched_skills", [])),
        missing_skills=json.dumps(result.get("missing_skills", [])),
        extra_skills=json.dumps(result.get("extra_skills", [])),
        summary=result.get("summary", "")
    )
    db.add(new_match)
    db.commit()
    db.refresh(new_match)

    return JobMatchResponse(
        match_score=new_match.match_score,
        matched_skills=json.loads(new_match.matched_skills),
        missing_skills=json.loads(new_match.missing_skills),
        extra_skills=json.loads(new_match.extra_skills),
        summary=new_match.summary
    )

# --- Recruitment Workflow Endpoint ---
from backend.workflows.recruitment_workflow import recruitment_workflow

class RecruitmentWorkflowRequest(BaseModel):
    candidate_id: int
    job_description: str

class RecruitmentWorkflowResponse(BaseModel):
    status: str
    message: str
    match_score: float
    recommendation: str
    skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]

@router.post("/recruitment/workflow", response_model=RecruitmentWorkflowResponse, tags=["recruitment"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
def execute_recruitment_workflow(
    request: RecruitmentWorkflowRequest,
    db: Session = Depends(get_db)
):
    if not request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
        
    candidate = candidate_repo.get(db, id=request.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
        
    if not candidate.resume_path:
        raise HTTPException(status_code=400, detail="Candidate has no resume attached.")
        
    initial_state = {
        "resume_path": candidate.resume_path,
        "jd_text": request.job_description,
        "resume_data": None,
        "extracted_skills": None,
        "job_requirements": None,
        "match_score": None,
        "recommendation": None,
        "final_report": None
    }
    
    try:
        final_state = recruitment_workflow.invoke(initial_state)
        
        # Save results to the database
        resume_data = final_state.get("resume_data") or {}
        report = final_state.get("final_report") or {}
        extracted_skills = final_state.get("extracted_skills") or []
        
        candidate_repo.update(db, db_obj=candidate, obj_in={
            "skills": json.dumps(extracted_skills),
            "experience": json.dumps(resume_data.get("experience", [])),
            "education": json.dumps(resume_data.get("education", [])),
            "projects": json.dumps(resume_data.get("projects", [])),
            "certifications": json.dumps(resume_data.get("certifications", [])),
            "matched_skills": json.dumps(report.get("matched_skills", [])),
            "missing_skills": json.dumps(report.get("missing_skills", [])),
            "match_score": final_state.get("match_score", 0.0),
            "score_breakdown": report.get("score_breakdown", "{}"),
            "recommendation": final_state.get("recommendation", ""),
            "current_company": resume_data.get("current_company"),
            "current_ctc": resume_data.get("current_ctc"),
            "expected_ctc": resume_data.get("expected_ctc"),
            "notice_period": resume_data.get("notice_period"),
            "preferred_location": resume_data.get("preferred_location"),
            "status": report.get("automated_decision", CandidateStatus.SCREENING.value)
        })
        
        return RecruitmentWorkflowResponse(
            status="success",
            message="Workflow completed and database updated.",
            match_score=final_state.get("match_score") or 0.0,
            recommendation=final_state.get("recommendation") or "",
            skills=extracted_skills,
            matched_skills=report.get("matched_skills") or [],
            missing_skills=report.get("missing_skills") or []
        )
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(e)}"
        )

# --- Chat Endpoints ---
class ChatRequest(BaseModel):
    candidate_id: Optional[int] = None
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db)):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    if not request.candidate_id or request.candidate_id == 0:
        reply = query_global_candidates(request.message, db)
        return ChatResponse(reply=reply)
    
    reply = query_candidate(request.message, request.candidate_id, db)
    return ChatResponse(reply=reply)

# --- Analytics Endpoint ---
@router.get("/analytics", tags=["analytics"], dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
def get_analytics(db: Session = Depends(get_db)):
    completed = db.query(Candidate).filter(Candidate.match_score.isnot(None)).count()
    failed = db.query(Candidate).filter(Candidate.recommendation.ilike("AI Analysis Failed%")).count()
    
    # Job Matching Statistics
    job_matches = db.query(JobMatch).all()
    total_matches = len(job_matches)
    
    if total_matches > 0:
        avg_match_score = sum(m.match_score for m in job_matches) / total_matches
        highest_match_score = max(m.match_score for m in job_matches)
        lowest_match_score = min(m.match_score for m in job_matches)
    else:
        avg_match_score = 0.0
        highest_match_score = 0.0
        lowest_match_score = 0.0
        
    # Analyze Top Matched & Missing Skills
    matched_skills_counts = {}
    missing_skills_counts = {}
    
    for m in job_matches:
        try:
            m_skills = json.loads(m.matched_skills)
            for s in m_skills:
                s_clean = s.strip()
                if s_clean:
                    matched_skills_counts[s_clean] = matched_skills_counts.get(s_clean, 0) + 1
        except Exception:
            pass
            
        try:
            miss_skills = json.loads(m.missing_skills)
            for s in miss_skills:
                s_clean = s.strip()
                if s_clean:
                    missing_skills_counts[s_clean] = missing_skills_counts.get(s_clean, 0) + 1
        except Exception:
            pass
            
    # Get top 5 sorted
    top_matched = sorted(matched_skills_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_missing = sorted(missing_skills_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    top_matched_list = [{"skill": k, "count": v} for k, v in top_matched]
    top_missing_list = [{"skill": k, "count": v} for k, v in top_missing]
    
    return {
        "average_resume_parsing_time_s": get_average_metric("parsing_time"),
        "ai_response_time_s": get_average_metric("llm_response_time"),
        "api_latency_s": get_average_metric("api_latency"),
        "analyses_completed": completed,
        "failed_analyses": failed,
        "cache_hit_rate_pct": 0.0,
        
        # New Job Matching Analytics
        "job_matching_stats": {
            "total_matches": total_matches,
            "average_score": round(avg_match_score, 2),
            "highest_score": round(highest_match_score, 2),
            "lowest_score": round(lowest_match_score, 2)
        },
        "job_matching_analysis": {
            "top_matched_skills": top_matched_list,
            "top_missing_skills": top_missing_list
        }
    }

# --- Admin Endpoints (Users & Logs) ---
@router.get("/admin/users", response_model=List[UserResponse], tags=["admin"], dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
def get_all_users(db: Session = Depends(get_db)):
    return user_repo.get_all(db)

@router.post("/admin/users", response_model=UserResponse, tags=["admin"], dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
def create_user(request: UserCreate, db: Session = Depends(get_db)):
    existing = user_repo.get_by_username(db, username=request.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pw = get_password_hash(request.password)
    new_user = user_repo.create(db, obj_in={
        "username": request.username,
        "hashed_password": hashed_pw,
        "role": request.role
    })
    return new_user

@router.put("/admin/users/{user_id}", response_model=UserResponse, tags=["admin"], dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
def update_user(user_id: int, request: UserUpdate, db: Session = Depends(get_db)):
    user = user_repo.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {}
    if request.role:
        update_data["role"] = request.role
    if request.password:
        update_data["hashed_password"] = get_password_hash(request.password)
        
    updated = user_repo.update(db, db_obj=user, obj_in=update_data)
    return updated

@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["admin"], dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = user_repo.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete super admin")
    user_repo.delete(db, id=user_id)
    return None

@router.get("/admin/logs", tags=["admin"], dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
def get_system_logs(lines: int = 100):
    if not os.path.exists(LOG_FILE):
        return {"logs": ["Log file not found."]}
    
    try:
        with open(LOG_FILE, "r") as f:
            all_lines = f.readlines()
            return {"logs": all_lines[-lines:]}
    except Exception as e:
        return {"logs": [f"Error reading logs: {str(e)}"]}

# --- Integrations Endpoints ---

@router.post("/integrations/zoho/sync/{candidate_id}", tags=["integrations"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def sync_zoho(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Mock integration delay
    await asyncio.sleep(1.5)
    zoho_id = f"ZOHO-REC-{random.randint(1000, 9999)}"

    updated = candidate_repo.update(db, db_obj=candidate, obj_in={"zoho_candidate_id": zoho_id})
    return {"status": "success", "zoho_candidate_id": zoho_id}

@router.post("/integrations/hackerearth/invite/{candidate_id}", tags=["integrations"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def invite_hackerearth(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Mock integration delay
    await asyncio.sleep(1.5)
    assessment_url = f"https://assess.hackerearth.com/test/{uuid.uuid4().hex[:8]}"
    score = random.randint(60, 95)

    updated = candidate_repo.update(db, db_obj=candidate, obj_in={
        "hackerearth_assessment_url": assessment_url,
        "hackerearth_score": score
    })
    return {"status": "success", "hackerearth_assessment_url": assessment_url, "hackerearth_score": score}

@router.post("/integrations/authbridge/bgv/{candidate_id}", tags=["integrations"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def initiate_bgv(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Mock integration delay
    await asyncio.sleep(1.5)
    status = "Pending"

    updated = candidate_repo.update(db, db_obj=candidate, obj_in={"authbridge_bgv_status": status})
    return {"status": "success", "authbridge_bgv_status": status}

@router.post("/integrations/keka/onboard/{candidate_id}", tags=["integrations"], dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def onboard_keka(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Mock integration delay
    await asyncio.sleep(1.5)
    keka_id = f"KEKA-EMP-{random.randint(100, 999)}"

    updated = candidate_repo.update(db, db_obj=candidate, obj_in={"keka_employee_id": keka_id})
    return {"status": "success", "keka_employee_id": keka_id}

@router.post(
    "/interviews/schedule",
    response_model=InterviewResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["interviews"],
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))]
)
def schedule_interview(
    request: InterviewCreate,
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(
        Candidate.id == request.candidate_id
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    interview = Interview(
        candidate_id=request.candidate_id,
        interviewer=request.interviewer,
        interview_date=request.interview_date,
        interview_time=request.interview_time,
        interview_mode=request.interview_mode,
        meeting_link=request.meeting_link,
        status="Scheduled"
    )

    db.add(interview)

    candidate.status = "Interview Scheduled"

    db.commit()
    db.refresh(interview)

    return interview

@router.get(
    "/interviews",
    response_model=List[InterviewResponse],
    tags=["interviews"],
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))]
)
def get_all_interviews(
    db: Session = Depends(get_db)
):
    interviews = db.query(Interview).order_by(Interview.id.desc()).all()
    return interviews    

@router.get(
    "/interviews/{interview_id}",
    response_model=InterviewResponse,
    tags=["interviews"],
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))]
)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(
        Interview.id == interview_id
    ).first()

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    return interview

@router.put(
    "/interviews/{interview_id}",
    response_model=InterviewResponse,
    tags=["interviews"],
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))]
)
def update_interview(
    interview_id: int,
    request: InterviewUpdate,
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(
        Interview.id == interview_id
    ).first()

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    update_data = request.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(interview, key, value)

    db.commit()
    db.refresh(interview)

    return interview

@router.delete(
    "/interviews/{interview_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["interviews"],
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))]
)
def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(
        Interview.id == interview_id
    ).first()

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    db.delete(interview)
    db.commit()

    return None

from backend.agents.communication_agent import generate_communication_template

class CommunicationRequest(BaseModel):
    email_type: str = Field(..., description="Type of email: invite, reject, offer")

@router.post(
    "/candidates/{candidate_id}/communication",
    response_model=dict,
    tags=["candidates"],
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))]
)
def generate_communication(
    candidate_id: int,
    request: CommunicationRequest,
    db: Session = Depends(get_db)
):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job_match = db.query(JobMatch).filter(JobMatch.candidate_id == candidate_id).order_by(JobMatch.id.desc()).first()
    
    candidate_data = {
        "name": candidate.name,
        "score": candidate.match_score or 0.0,
        "matched_skills": json.loads(job_match.matched_skills) if job_match else [],
        "missing_skills": json.loads(job_match.missing_skills) if job_match else []
    }
    
    email_content = generate_communication_template(candidate_data, request.email_type)
    
    return {"email_content": email_content}
