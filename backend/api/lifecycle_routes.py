from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.postgres import get_db
from backend.api.deps import get_current_user, RoleChecker
from backend.database.models import (
    UserRole, Job, RecruitmentStage, Application, Interview,
    InterviewFeedback, Assessment, AssessmentResult, Offer,
    Onboarding, CommunicationHistory, ActivityLog, Candidate
)
from backend.schemas.lifecycle_schemas import (
    JobCreate, JobUpdate, JobResponse,
    RecruitmentStageCreate, RecruitmentStageResponse,
    ApplicationCreate, ApplicationUpdate, ApplicationResponse,
    InterviewCreate, InterviewUpdate, InterviewResponse,
    InterviewFeedbackCreate, InterviewFeedbackResponse,
    AssessmentCreate, AssessmentResponse,
    AssessmentResultCreate, AssessmentResultResponse,
    OfferCreate, OfferUpdate, OfferResponse,
    OnboardingCreate, OnboardingUpdate, OnboardingResponse,
    CommunicationHistoryCreate, CommunicationHistoryResponse,
    ActivityLogCreate, ActivityLogResponse
)
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["recruitment-lifecycle"])

def create_activity_log(
    db: Session, performer: str, action: str, candidate_id: Optional[int] = None,
    application_id: Optional[int] = None, details: Optional[str] = None
):
    log = ActivityLog(
        performer=performer,
        action=action,
        candidate_id=candidate_id,
        application_id=application_id,
        details=details
    )
    db.add(log)
    db.commit()
    return log

# --- Jobs & Stages ---

@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    new_job = Job(
        title=job_in.title,
        department=job_in.department,
        location=job_in.location,
        description=job_in.description,
        requirements=job_in.requirements,
        status=job_in.status
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # Add default or provided stages
    default_stages = ["Screening", "Assessment", "Interview", "HR Interview", "Offer", "Onboarding"]
    stages_to_add = job_in.stages or [
        RecruitmentStageCreate(name=st, stage_order=idx + 1, is_default=True)
        for idx, st in enumerate(default_stages)
    ]

    for st_in in stages_to_add:
        stage_obj = RecruitmentStage(
            job_id=new_job.id,
            name=st_in.name,
            stage_order=st_in.stage_order,
            is_default=st_in.is_default
        )
        db.add(stage_obj)

    db.commit()
    db.refresh(new_job)

    create_activity_log(db, performer=current_user, action="JOB_CREATED", details=f"Job '{new_job.title}' created.")
    return new_job

@router.get("/jobs", response_model=List[JobResponse])
def get_jobs(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    query = db.query(Job)
    if status_filter:
        query = query.filter(Job.status == status_filter)
    return query.order_by(Job.created_at.desc()).all()

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/jobs/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_in: JobUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = job_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    create_activity_log(db, performer=current_user, action="JOB_UPDATED", details=f"Job {job_id} updated.")
    return job

@router.post("/jobs/{job_id}/stages", response_model=RecruitmentStageResponse)
def add_job_stage(
    job_id: int,
    stage_in: RecruitmentStageCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    stage_obj = RecruitmentStage(
        job_id=job_id,
        name=stage_in.name,
        stage_order=stage_in.stage_order,
        is_default=stage_in.is_default
    )
    db.add(stage_obj)
    db.commit()
    db.refresh(stage_obj)

    create_activity_log(db, performer=current_user, action="STAGE_ADDED", details=f"Stage '{stage_in.name}' added to job {job_id}.")
    return stage_obj

# --- Applications ---

@router.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    app_in: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    candidate = db.query(Candidate).filter(Candidate.id == app_in.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    app_obj = Application(
        candidate_id=app_in.candidate_id,
        job_id=app_in.job_id,
        source=app_in.source,
        current_stage_id=app_in.current_stage_id,
        stage_name=app_in.stage_name,
        status=app_in.status
    )
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)

    create_activity_log(
        db, performer=current_user, action="APPLICATION_CREATED",
        candidate_id=app_in.candidate_id, application_id=app_obj.id,
        details=f"Application created for job {app_in.job_id or 'General'}"
    )
    return app_obj

@router.get("/applications", response_model=List[ApplicationResponse])
def get_applications(
    candidate_id: Optional[int] = None,
    job_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    query = db.query(Application)
    if candidate_id:
        query = query.filter(Application.candidate_id == candidate_id)
    if job_id:
        query = query.filter(Application.job_id == job_id)
    if status_filter:
        query = query.filter(Application.status == status_filter)
    return query.order_by(Application.applied_date.desc()).all()

@router.get("/applications/{app_id}", response_model=ApplicationResponse)
def get_application(
    app_id: int,
    db: Session = Depends(get_db),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    app_obj = db.query(Application).filter(Application.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_obj

@router.put("/applications/{app_id}", response_model=ApplicationResponse)
def update_application(
    app_id: int,
    app_in: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    app_obj = db.query(Application).filter(Application.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = app_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(app_obj, field, value)

    db.commit()
    db.refresh(app_obj)

    create_activity_log(
        db, performer=current_user, action="APPLICATION_UPDATED",
        candidate_id=app_obj.candidate_id, application_id=app_obj.id,
        details=f"Application {app_id} stage set to '{app_obj.stage_name}', status '{app_obj.status}'"
    )
    return app_obj

# --- Interviews & Feedback ---

@router.post("/interviews", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
def schedule_interview(
    interview_in: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    candidate = db.query(Candidate).filter(Candidate.id == interview_in.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    interview_obj = Interview(
        candidate_id=interview_in.candidate_id,
        application_id=interview_in.application_id,
        interviewer=interview_in.interviewer,
        scheduled_at=interview_in.scheduled_at,
        interview_type=interview_in.interview_type,
        status=interview_in.status,
        meeting_link=interview_in.meeting_link
    )
    db.add(interview_obj)

    # Automatically update candidate status to Interview Scheduled
    candidate.status = "Interview Scheduled"

    db.commit()
    db.refresh(interview_obj)

    create_activity_log(
        db, performer=current_user, action="INTERVIEW_SCHEDULED",
        candidate_id=interview_in.candidate_id, application_id=interview_in.application_id,
        details=f"{interview_in.interview_type} interview scheduled with {interview_in.interviewer}"
    )
    return interview_obj

@router.get("/interviews", response_model=List[InterviewResponse])
def get_interviews(
    candidate_id: Optional[int] = None,
    application_id: Optional[int] = None,
    db: Session = Depends(get_db),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    query = db.query(Interview)
    if candidate_id:
        query = query.filter(Interview.candidate_id == candidate_id)
    if application_id:
        query = query.filter(Interview.application_id == application_id)
    return query.order_by(Interview.scheduled_at.desc()).all()

@router.put("/interviews/{interview_id}", response_model=InterviewResponse)
def update_interview(
    interview_id: int,
    interview_in: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    interview_obj = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview_obj:
        raise HTTPException(status_code=404, detail="Interview not found")

    update_data = interview_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interview_obj, field, value)

    db.commit()
    db.refresh(interview_obj)

    create_activity_log(
        db, performer=current_user, action="INTERVIEW_UPDATED",
        candidate_id=interview_obj.candidate_id, application_id=interview_obj.application_id,
        details=f"Interview {interview_id} status updated to {interview_obj.status}"
    )
    return interview_obj

@router.post("/interviews/{interview_id}/feedback", response_model=InterviewFeedbackResponse)
def add_interview_feedback(
    interview_id: int,
    feedback_in: InterviewFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    interview_obj = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview_obj:
        raise HTTPException(status_code=404, detail="Interview not found")

    feedback_obj = InterviewFeedback(
        interview_id=interview_id,
        interviewer=feedback_in.interviewer or current_user,
        feedback=feedback_in.feedback,
        rating=feedback_in.rating,
        recommendation=feedback_in.recommendation
    )
    db.add(feedback_obj)
    interview_obj.status = "Completed"

    db.commit()
    db.refresh(feedback_obj)

    create_activity_log(
        db, performer=current_user, action="INTERVIEW_FEEDBACK_ADDED",
        candidate_id=interview_obj.candidate_id, application_id=interview_obj.application_id,
        details=f"Feedback submitted for interview {interview_id}. Rating: {feedback_in.rating}/5.0"
    )
    return feedback_obj

# --- Assessments ---

@router.post("/assessments", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    assessment_in: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    assessment_obj = Assessment(
        title=assessment_in.title,
        description=assessment_in.description,
        assessment_type=assessment_in.assessment_type,
        max_score=assessment_in.max_score,
        passing_score=assessment_in.passing_score
    )
    db.add(assessment_obj)
    db.commit()
    db.refresh(assessment_obj)
    return assessment_obj

@router.get("/assessments", response_model=List[AssessmentResponse])
def get_assessments(
    db: Session = Depends(get_db),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    return db.query(Assessment).order_by(Assessment.created_at.desc()).all()

@router.post("/assessment-results", response_model=AssessmentResultResponse, status_code=status.HTTP_201_CREATED)
def record_assessment_result(
    result_in: AssessmentResultCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    result_obj = AssessmentResult(
        assessment_id=result_in.assessment_id,
        candidate_id=result_in.candidate_id,
        application_id=result_in.application_id,
        score=result_in.score,
        result=result_in.result,
        feedback=result_in.feedback
    )
    db.add(result_obj)
    db.commit()
    db.refresh(result_obj)

    create_activity_log(
        db, performer=current_user, action="ASSESSMENT_SUBMITTED",
        candidate_id=result_in.candidate_id, application_id=result_in.application_id,
        details=f"Assessment score: {result_in.score}, Result: {result_in.result}"
    )
    return result_obj

# --- Offers ---

@router.post("/offers", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
def create_offer(
    offer_in: OfferCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    candidate = db.query(Candidate).filter(Candidate.id == offer_in.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    offer_obj = Offer(
        candidate_id=offer_in.candidate_id,
        application_id=offer_in.application_id,
        salary=offer_in.salary,
        currency=offer_in.currency,
        joining_date=offer_in.joining_date,
        status=offer_in.status
    )
    db.add(offer_obj)

    if offer_in.status == "Sent":
        offer_obj.sent_date = datetime.now()
        candidate.status = "Offer Sent"

    db.commit()
    db.refresh(offer_obj)

    create_activity_log(
        db, performer=current_user, action="OFFER_CREATED",
        candidate_id=offer_in.candidate_id, application_id=offer_in.application_id,
        details=f"Offer created. Salary: {offer_in.currency} {offer_in.salary}"
    )
    return offer_obj

@router.get("/offers", response_model=List[OfferResponse])
def get_offers(
    candidate_id: Optional[int] = None,
    db: Session = Depends(get_db),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    query = db.query(Offer)
    if candidate_id:
        query = query.filter(Offer.candidate_id == candidate_id)
    return query.order_by(Offer.created_at.desc()).all()

@router.put("/offers/{offer_id}", response_model=OfferResponse)
def update_offer(
    offer_id: int,
    offer_in: OfferUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    offer_obj = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer_obj:
        raise HTTPException(status_code=404, detail="Offer not found")

    update_data = offer_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(offer_obj, field, value)

    candidate = db.query(Candidate).filter(Candidate.id == offer_obj.candidate_id).first()
    if offer_obj.status == "Accepted" and candidate:
        candidate.status = "Hired"
        offer_obj.accepted_rejected_date = datetime.now()
    elif offer_obj.status == "Rejected":
        offer_obj.accepted_rejected_date = datetime.now()

    db.commit()
    db.refresh(offer_obj)

    create_activity_log(
        db, performer=current_user, action="OFFER_UPDATED",
        candidate_id=offer_obj.candidate_id, application_id=offer_obj.application_id,
        details=f"Offer {offer_id} status changed to {offer_obj.status}"
    )
    return offer_obj

# --- Onboarding ---

@router.post("/onboarding", response_model=OnboardingResponse, status_code=status.HTTP_201_CREATED)
def create_onboarding(
    onboarding_in: OnboardingCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    candidate = db.query(Candidate).filter(Candidate.id == onboarding_in.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    onboard_obj = Onboarding(
        candidate_id=onboarding_in.candidate_id,
        application_id=onboarding_in.application_id,
        joining_status=onboarding_in.joining_status,
        document_verification=onboarding_in.document_verification,
        background_check_status=onboarding_in.background_check_status,
        joining_date=onboarding_in.joining_date,
        notes=onboarding_in.notes
    )
    db.add(onboard_obj)
    db.commit()
    db.refresh(onboard_obj)

    create_activity_log(
        db, performer=current_user, action="ONBOARDING_INITIATED",
        candidate_id=onboarding_in.candidate_id, application_id=onboarding_in.application_id,
        details=f"Onboarding record created for candidate {onboarding_in.candidate_id}"
    )
    return onboard_obj

@router.get("/onboarding", response_model=List[OnboardingResponse])
def get_onboarding_records(
    candidate_id: Optional[int] = None,
    db: Session = Depends(get_db),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    query = db.query(Onboarding)
    if candidate_id:
        query = query.filter(Onboarding.candidate_id == candidate_id)
    return query.order_by(Onboarding.created_at.desc()).all()

@router.put("/onboarding/{onboarding_id}", response_model=OnboardingResponse)
def update_onboarding(
    onboarding_id: int,
    onboard_in: OnboardingUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    onboard_obj = db.query(Onboarding).filter(Onboarding.id == onboarding_id).first()
    if not onboard_obj:
        raise HTTPException(status_code=404, detail="Onboarding record not found")

    update_data = onboard_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(onboard_obj, field, value)

    db.commit()
    db.refresh(onboard_obj)

    create_activity_log(
        db, performer=current_user, action="ONBOARDING_UPDATED",
        candidate_id=onboard_obj.candidate_id, application_id=onboard_obj.application_id,
        details=f"Onboarding {onboarding_id} updated. Joining status: {onboard_obj.joining_status}"
    )
    return onboard_obj

# --- Communications & Activity Logs ---

@router.post("/communications", response_model=CommunicationHistoryResponse, status_code=status.HTTP_201_CREATED)
def record_communication(
    comm_in: CommunicationHistoryCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
):
    comm_obj = CommunicationHistory(
        candidate_id=comm_in.candidate_id,
        sender=comm_in.sender or current_user,
        recipient=comm_in.recipient,
        communication_type=comm_in.communication_type,
        subject=comm_in.subject,
        message=comm_in.message
    )
    db.add(comm_obj)
    db.commit()
    db.refresh(comm_obj)

    create_activity_log(
        db, performer=current_user, action="COMMUNICATION_SENT",
        candidate_id=comm_in.candidate_id,
        details=f"{comm_in.communication_type} sent to {comm_in.recipient}"
    )
    return comm_obj

@router.get("/candidates/{candidate_id}/communications", response_model=List[CommunicationHistoryResponse])
def get_candidate_communications(
    candidate_id: int,
    db: Session = Depends(get_db),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    return db.query(CommunicationHistory).filter(CommunicationHistory.candidate_id == candidate_id).order_by(CommunicationHistory.sent_at.desc()).all()

@router.get("/activity-logs", response_model=List[ActivityLogResponse])
def get_activity_logs(
    candidate_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    role: UserRole = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.HIRING_MANAGER]))
):
    query = db.query(ActivityLog)
    if candidate_id:
        query = query.filter(ActivityLog.candidate_id == candidate_id)
    return query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
