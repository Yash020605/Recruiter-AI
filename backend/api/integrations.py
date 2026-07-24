from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.postgres import get_db
from backend.tools.candidate_database import candidate_repo
from backend.database.models import UserRole
from backend.api.deps import RoleChecker

from backend.integrations.naukri.client import import_candidate_profile
from backend.integrations.zoho.client import sync_candidate_to_ats
from backend.integrations.keka.client import onboard_employee
from backend.integrations.hackerearth.client import invite_to_assessment, get_assessment_score
from backend.integrations.authbridge.client import initiate_bgv, poll_bgv_status

from backend.integrations.linkedin.client import import_linkedin_profile
from backend.integrations.github.client import analyze_github_profile
from backend.integrations.calendar.client import schedule_calendar_interview
from backend.integrations.google_sheets.client import export_to_google_sheets

from pydantic import BaseModel

router = APIRouter()

class NaukriImportRequest(BaseModel):
    profile_url: str

@router.post("/naukri/import", dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def trigger_naukri_import(request: NaukriImportRequest, db: Session = Depends(get_db)):
    response = await import_candidate_profile(request.profile_url)
    
    if response["status"] == "success":
        # Create a candidate record
        new_candidate = candidate_repo.create(db, obj_in={
            "name": response["data"]["name"],
            "email": response["data"]["email"],
            "phone": response["data"]["phone"],
            "current_company": response["data"]["current_company"],
            "skills": f'["{response["data"]["skills"].replace(", ", "\\\", \\\"")}"]',
            "resume_path": "Naukri Profile"
        })
        return {"status": "success", "candidate_id": new_candidate.id, "message": "Candidate imported successfully"}
    
    return response

@router.post("/zoho/sync/{candidate_id}", dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def trigger_zoho_sync(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    candidate_data = {"name": candidate.name, "email": candidate.email}
    response = await sync_candidate_to_ats(candidate_data)
    
    if response["status"] == "success":
        candidate_repo.update(db, db_obj=candidate, obj_in={"zoho_candidate_id": response["zoho_candidate_id"]})
        
    return response

@router.post("/keka/onboard/{candidate_id}", dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def trigger_keka_onboard(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    candidate_data = {"name": candidate.name, "email": candidate.email}
    response = await onboard_employee(candidate_data)
    
    if response["status"] == "success":
        candidate_repo.update(db, db_obj=candidate, obj_in={"keka_employee_id": response["keka_employee_id"]})
        
    return response

@router.post("/hackerearth/invite/{candidate_id}", dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def trigger_hackerearth_invite(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    response = await invite_to_assessment(candidate.email or f"candidate{candidate_id}@example.com", "TEST-123")
    
    if response["status"] == "success":
        candidate_repo.update(db, db_obj=candidate, obj_in={"hackerearth_assessment_url": response["assessment_url"]})
        
    return response

@router.post("/authbridge/bgv/{candidate_id}", dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def trigger_authbridge_bgv(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    candidate_data = {"name": candidate.name, "email": candidate.email}
    response = await initiate_bgv(candidate_data)
    
    if response["status"] == "success":
        candidate_repo.update(db, db_obj=candidate, obj_in={"authbridge_bgv_status": response["bgv_status"]})
        
    return response

class LinkedinImportRequest(BaseModel):
    profile_url: str

@router.post("/linkedin/import", dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def trigger_linkedin_import(request: LinkedinImportRequest, db: Session = Depends(get_db)):
    try:
        data = await import_linkedin_profile(request.profile_url)
        name = data.get("full_name") or "Unknown"
        email = f"{data.get('public_identifier', 'candidate')}@example.com"
        company = data.get("occupation")
        skills = data.get("skills", [])
        
        new_candidate = candidate_repo.create(db, obj_in={
            "name": name,
            "email": email,
            "current_company": company,
            "skills": str(skills),
            "linkedin_profile_url": request.profile_url,
            "resume_path": "LinkedIn Profile"
        })
        return {"status": "success", "candidate_id": new_candidate.id, "message": "LinkedIn profile imported successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GithubAnalyzeRequest(BaseModel):
    github_username: str

@router.post("/github/analyze/{candidate_id}", dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def trigger_github_analyze(candidate_id: int, request: GithubAnalyzeRequest, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    try:
        score = await analyze_github_profile(request.github_username)
        candidate_repo.update(db, db_obj=candidate, obj_in={"github_score": score})
        return {"status": "success", "score": score, "message": "Analyzed GitHub profile"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ScheduleCalendarRequest(BaseModel):
    start_time_iso: str

@router.post("/calendar/schedule/{candidate_id}", dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def trigger_calendar_schedule(candidate_id: int, request: ScheduleCalendarRequest, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    try:
        res = await schedule_calendar_interview(
            email=candidate.email or f"candidate{candidate_id}@example.com", 
            name=candidate.name or "Candidate",
            start_time_iso=request.start_time_iso
        )
        if res.get("jitsi_url"):
            # Reuse the existing DB columns
            candidate_repo.update(db, db_obj=candidate, obj_in={
                "google_meet_url": res["jitsi_url"],
                "calendly_interview_time": res["event_id"]
            })
            return {"status": "success", "meet_url": res["jitsi_url"], "event_id": res["event_id"]}
        raise HTTPException(status_code=500, detail="Failed to generate Calendar link")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/google-sheets/export/{candidate_id}", dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))])
async def trigger_google_sheets_export(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    try:
        candidate_data = {"id": candidate.id, "name": candidate.name, "score": candidate.match_score}
        res = await export_to_google_sheets(candidate_data)
        if res.get("status") == "success":
            candidate_repo.update(db, db_obj=candidate, obj_in={"google_sheets_sync_status": "Synced"})
            return {"status": "success", "message": "Exported to Google Sheets"}
        raise HTTPException(status_code=500, detail="Failed to export to Google Sheets")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
