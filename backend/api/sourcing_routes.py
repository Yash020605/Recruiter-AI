from typing import List, Optional
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.database.postgres import get_db
from backend.api.deps import get_current_user, RoleChecker
from backend.database.models import (
    UserRole, Candidate, CandidateSource, SocialProfile, CandidatePipeline, CandidateJourney
)
from backend.schemas.sourcing_schemas import (
    SourcedCandidateCreate, SourcedCandidateResponse, SourcedCandidateRankRequest,
    SocialProfileCreate, SocialProfileUpdate, SocialProfileResponse,
    CandidateSourceCreate, CandidateSourceResponse,
    CandidatePipelineUpdate, CandidatePipelineResponse
)
from backend.integrations.github_client import fetch_github_user_profile
from backend.workflows.recruiter_graph import recruiter_graph
from backend.api.lifecycle_routes import create_activity_log
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/sourcing", tags=["candidate-sourcing"])

@router.post("/candidates", response_model=SourcedCandidateResponse, status_code=status.HTTP_201_CREATED)
async def add_sourced_candidate(
    payload: SourcedCandidateCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    # 1. Create candidate record
    candidate = Candidate(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        current_company=payload.current_company,
        preferred_location=payload.preferred_location,
        skills=payload.skills,
        experience=payload.experience,
        education=payload.education,
        status="New",
        resume_path=f"Sourced via {payload.source_platform}"
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    # 2. Add CandidateSource record
    source_obj = CandidateSource(
        candidate_id=candidate.id,
        source_platform=payload.source_platform,
        source_url=payload.source_url,
        recruiter=payload.recruiter or current_user
    )
    db.add(source_obj)

    # 3. Add CandidatePipeline initial state (Discovered)
    pipeline_obj = CandidatePipeline(
        candidate_id=candidate.id,
        source=payload.source_platform,
        stage="Discovered",
        recruiter=payload.recruiter or current_user,
        notes=payload.initial_notes
    )
    db.add(pipeline_obj)

    # Add journey event
    journey_obj = CandidateJourney(
        candidate_id=candidate.id,
        stage="Discovered",
        status="Completed",
        remarks=f"Sourced from {payload.source_platform}",
        updated_by=current_user
    )
    db.add(journey_obj)

    # 4. Handle initial social profiles if provided or if platform is GitHub/LinkedIn
    if payload.social_profiles:
        for p in payload.social_profiles:
            sp_data = p.model_dump()
            if p.platform.lower() == "github" and p.username:
                gh_info = await fetch_github_user_profile(p.username)
                sp_data.update({
                    "bio": gh_info.get("bio") or p.bio,
                    "location": gh_info.get("location") or p.location,
                    "followers": gh_info.get("followers", 0),
                    "repositories_count": gh_info.get("repositories_count", 0),
                    "top_languages": gh_info.get("top_languages"),
                    "total_stars": gh_info.get("total_stars", 0),
                    "raw_data": gh_info.get("raw_data")
                })
            sp_obj = SocialProfile(candidate_id=candidate.id, **sp_data)
            db.add(sp_obj)
    elif payload.source_url and "github.com/" in payload.source_url.lower():
        username = payload.source_url.strip("/").split("/")[-1]
        gh_info = await fetch_github_user_profile(username)
        sp_obj = SocialProfile(
            candidate_id=candidate.id,
            platform="GitHub",
            profile_url=payload.source_url,
            username=username,
            bio=gh_info.get("bio"),
            location=gh_info.get("location"),
            followers=gh_info.get("followers", 0),
            repositories_count=gh_info.get("repositories_count", 0),
            top_languages=gh_info.get("top_languages"),
            total_stars=gh_info.get("total_stars", 0),
            raw_data=gh_info.get("raw_data")
        )
        db.add(sp_obj)

    db.commit()
    db.refresh(candidate)

    create_activity_log(
        db, performer=current_user, action="CANDIDATE_SOURCED",
        candidate_id=candidate.id,
        details=f"Candidate '{candidate.name}' sourced from {payload.source_platform}"
    )

    return candidate

@router.put("/candidates/{candidate_id}/source", response_model=CandidateSourceResponse)
def update_candidate_source(
    candidate_id: int,
    source_in: CandidateSourceCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    source_obj = db.query(CandidateSource).filter(CandidateSource.candidate_id == candidate_id).first()
    if source_obj:
        source_obj.source_platform = source_in.source_platform
        source_obj.source_url = source_in.source_url
        source_obj.recruiter = source_in.recruiter or current_user
    else:
        source_obj = CandidateSource(
            candidate_id=candidate_id,
            source_platform=source_in.source_platform,
            source_url=source_in.source_url,
            recruiter=source_in.recruiter or current_user
        )
        db.add(source_obj)

    db.commit()
    db.refresh(source_obj)

    create_activity_log(
        db, performer=current_user, action="SOURCE_UPDATED",
        candidate_id=candidate_id,
        details=f"Source updated to {source_in.source_platform}"
    )
    return source_obj

@router.post("/candidates/{candidate_id}/social-profile", response_model=SocialProfileResponse)
async def add_social_profile(
    candidate_id: int,
    profile_in: SocialProfileCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    sp_data = profile_in.model_dump()
    if profile_in.platform.lower() == "github":
        username = profile_in.username
        if not username and "github.com/" in profile_in.profile_url:
            username = profile_in.profile_url.strip("/").split("/")[-1]
        if username:
            gh_info = await fetch_github_user_profile(username)
            sp_data.update({
                "username": username,
                "bio": gh_info.get("bio") or profile_in.bio,
                "location": gh_info.get("location") or profile_in.location,
                "followers": gh_info.get("followers", 0),
                "repositories_count": gh_info.get("repositories_count", 0),
                "top_languages": gh_info.get("top_languages"),
                "total_stars": gh_info.get("total_stars", 0),
                "raw_data": gh_info.get("raw_data")
            })

    sp_obj = SocialProfile(candidate_id=candidate_id, **sp_data)
    db.add(sp_obj)
    db.commit()
    db.refresh(sp_obj)

    create_activity_log(
        db, performer=current_user, action="SOCIAL_PROFILE_ADDED",
        candidate_id=candidate_id,
        details=f"{profile_in.platform} profile added."
    )
    return sp_obj

@router.put("/social-profile/{profile_id}", response_model=SocialProfileResponse)
def update_social_profile(
    profile_id: int,
    profile_in: SocialProfileUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    sp_obj = db.query(SocialProfile).filter(SocialProfile.id == profile_id).first()
    if not sp_obj:
        raise HTTPException(status_code=404, detail="Social profile not found")

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sp_obj, field, value)

    db.commit()
    db.refresh(sp_obj)
    return sp_obj

@router.get("/candidates", response_model=List[SourcedCandidateResponse])
def search_sourced_candidates(
    source_platform: Optional[str] = None,
    skills: Optional[str] = None,
    location: Optional[str] = None,
    min_experience: Optional[float] = None,
    stage: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    query = db.query(Candidate)

    if source_platform:
        query = query.join(Candidate.sources).filter(CandidateSource.source_platform.ilike(f"%{source_platform}%"))

    if skills:
        query = query.filter(
            or_(
                Candidate.skills.ilike(f"%{skills}%"),
                Candidate.matched_skills.ilike(f"%{skills}%")
            )
        )

    if location:
        query = query.filter(Candidate.preferred_location.ilike(f"%{location}%"))

    if min_experience is not None:
        query = query.filter(Candidate.total_experience_years >= min_experience)

    if stage:
        query = query.join(Candidate.pipeline_records).filter(CandidatePipeline.stage == stage)

    if search:
        query = query.filter(
            or_(
                Candidate.name.ilike(f"%{search}%"),
                Candidate.email.ilike(f"%{search}%"),
                Candidate.current_company.ilike(f"%{search}%")
            )
        )

    return query.order_by(Candidate.id.desc()).all()

@router.put("/candidates/{candidate_id}/pipeline", response_model=CandidatePipelineResponse)
def move_candidate_pipeline(
    candidate_id: int,
    pipeline_in: CandidatePipelineUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    pipeline_obj = db.query(CandidatePipeline).filter(CandidatePipeline.candidate_id == candidate_id).order_by(CandidatePipeline.updated_at.desc()).first()

    new_stage = pipeline_in.stage or (pipeline_obj.stage if pipeline_obj else "Discovered")
    source_name = pipeline_obj.source if pipeline_obj else "Unknown"

    new_pipeline = CandidatePipeline(
        candidate_id=candidate_id,
        source=source_name,
        stage=new_stage,
        recruiter=pipeline_in.recruiter or current_user,
        notes=pipeline_in.notes or (pipeline_obj.notes if pipeline_obj else None)
    )
    db.add(new_pipeline)

    # Sync candidate main status if applicable
    if new_stage in ["Applied", "Interview", "Offer", "Hired"]:
        candidate.status = new_stage

    # Log Journey event
    journey_obj = CandidateJourney(
        candidate_id=candidate_id,
        stage=new_stage,
        status="Completed",
        remarks=f"Pipeline moved to {new_stage}. Notes: {pipeline_in.notes or 'N/A'}",
        updated_by=current_user
    )
    db.add(journey_obj)

    db.commit()
    db.refresh(new_pipeline)

    create_activity_log(
        db, performer=current_user, action="PIPELINE_STAGE_CHANGED",
        candidate_id=candidate_id,
        details=f"Candidate moved to pipeline stage '{new_stage}'"
    )

    return new_pipeline

@router.get("/candidates/{candidate_id}/history")
def get_candidate_sourcing_history(
    candidate_id: int,
    db: Session = Depends(get_db),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    sources = db.query(CandidateSource).filter(CandidateSource.candidate_id == candidate_id).all()
    profiles = db.query(SocialProfile).filter(SocialProfile.candidate_id == candidate_id).all()
    pipeline_records = db.query(CandidatePipeline).filter(CandidatePipeline.candidate_id == candidate_id).order_by(CandidatePipeline.updated_at.desc()).all()
    journeys = db.query(CandidateJourney).filter(CandidateJourney.candidate_id == candidate_id).order_by(CandidateJourney.created_at.asc()).all()

    return {
        "candidate_id": candidate_id,
        "name": candidate.name,
        "sources": sources,
        "social_profiles": profiles,
        "pipeline_history": pipeline_records,
        "journey_history": journeys
    }

@router.post("/candidates/{candidate_id}/rank")
def rank_sourced_candidate(
    candidate_id: int,
    payload: SourcedCandidateRankRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Reuse existing LangGraph multi-agent analysis workflow
    initial_state = {
        "candidate_id": candidate_id,
        "resume_text": f"Name: {candidate.name}\nSkills: {candidate.skills or ''}\nExperience: {candidate.experience or ''}\nEducation: {candidate.education or ''}\nCompany: {candidate.current_company or ''}",
        "job_description": payload.job_description,
        "extracted_skills": [],
        "match_score": 0.0,
        "matched_skills": [],
        "missing_skills": [],
        "recommendation": "",
        "status": "pending",
        "error": None
    }

    try:
        result = recruiter_graph.invoke(initial_state)

        # Update candidate with match score & recommendation
        candidate.match_score = result.get("match_score", 0.0)
        candidate.matched_skills = json.dumps(result.get("matched_skills", []))
        candidate.missing_skills = json.dumps(result.get("missing_skills", []))
        candidate.recommendation = result.get("recommendation", "")

        db.commit()
        db.refresh(candidate)

        create_activity_log(
            db, performer=current_user, action="CANDIDATE_RANKED",
            candidate_id=candidate_id,
            details=f"AI Rank calculated for candidate '{candidate.name}'. Score: {candidate.match_score}%"
        )

        return {
            "status": "success",
            "candidate_id": candidate_id,
            "match_score": candidate.match_score,
            "matched_skills": result.get("matched_skills", []),
            "missing_skills": result.get("missing_skills", []),
            "recommendation": candidate.recommendation
        }
    except Exception as e:
        logger.error(f"Error ranking sourced candidate {candidate_id}: {e}")
        # Fallback keyword matching calculation if LLM call fails
        jd_words = set(payload.job_description.lower().split())
        cand_skills = set((candidate.skills or "").lower().split(","))
        matched = list(cand_skills.intersection(jd_words))
        missing = list(cand_skills - jd_words)
        score = min(100.0, float(len(matched) * 20.0 + 30.0))

        candidate.match_score = score
        candidate.matched_skills = json.dumps(matched)
        candidate.recommendation = f"Recommended (Score: {score}%)"
        db.commit()

        return {
            "status": "success",
            "candidate_id": candidate_id,
            "match_score": score,
            "matched_skills": matched,
            "missing_skills": missing,
            "recommendation": candidate.recommendation
        }
