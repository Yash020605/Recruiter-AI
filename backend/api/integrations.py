
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database.postgres import get_db
from backend.tools.candidate_database import candidate_repo
from backend.database.models import UserRole
from backend.api.deps import RoleChecker

from backend.integrations.naukri.client import import_candidate_profile
from backend.integrations.zoho.client import sync_candidate_to_ats
from backend.integrations.keka.client import onboard_employee
from backend.integrations.hackerearth.client import (
    invite_to_assessment,
    get_assessment_score,
)
from backend.integrations.authbridge.client import (
    initiate_bgv,
    poll_bgv_status,
)


router = APIRouter()


# ============================================================
# Naukri Import
# ============================================================

class NaukriImportRequest(BaseModel):
    profile_url: str


@router.post(
    "/naukri/import",
    dependencies=[
        Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
    ],
)
async def trigger_naukri_import(
    request: NaukriImportRequest,
    db: Session = Depends(get_db),
):
    response = await import_candidate_profile(request.profile_url)

    if response["status"] == "success":
        data = response["data"]

        # Convert comma-separated skills into a proper JSON array.
        raw_skills = data.get("skills", "")

        if isinstance(raw_skills, str):
            skills_list = [
                skill.strip()
                for skill in raw_skills.split(",")
                if skill.strip()
            ]
        elif isinstance(raw_skills, list):
            skills_list = raw_skills
        else:
            skills_list = []

        new_candidate = candidate_repo.create(
            db,
            obj_in={
                "name": data.get("name"),
                "email": data.get("email"),
                "phone": data.get("phone"),
                "current_company": data.get("current_company"),
                "skills": json.dumps(skills_list),
                "resume_path": "Naukri Profile",
            },
        )

        return {
            "status": "success",
            "candidate_id": new_candidate.id,
            "message": "Candidate imported successfully",
        }

    return response


# ============================================================
# Zoho Sync
# ============================================================

@router.post(
    "/zoho/sync/{candidate_id}",
    dependencies=[
        Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
    ],
)
async def trigger_zoho_sync(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    candidate = candidate_repo.get(db, id=candidate_id)

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    candidate_data = {
        "name": candidate.name,
        "email": candidate.email,
    }

    response = await sync_candidate_to_ats(candidate_data)

    if response["status"] == "success":
        candidate_repo.update(
            db,
            db_obj=candidate,
            obj_in={
                "zoho_candidate_id": response["zoho_candidate_id"]
            },
        )

    return response


# ============================================================
# Keka Onboarding
# ============================================================

@router.post(
    "/keka/onboard/{candidate_id}",
    dependencies=[
        Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
    ],
)
async def trigger_keka_onboard(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    candidate = candidate_repo.get(db, id=candidate_id)

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    candidate_data = {
        "name": candidate.name,
        "email": candidate.email,
    }

    response = await onboard_employee(candidate_data)

    if response["status"] == "success":
        candidate_repo.update(
            db,
            db_obj=candidate,
            obj_in={
                "keka_employee_id": response["keka_employee_id"]
            },
        )

    return response


# ============================================================
# HackerEarth Assessment Invitation
# ============================================================

@router.post(
    "/hackerearth/invite/{candidate_id}",
    dependencies=[
        Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
    ],
)
async def trigger_hackerearth_invite(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    candidate = candidate_repo.get(db, id=candidate_id)

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    email = (
        candidate.email
        or f"candidate{candidate_id}@example.com"
    )

    response = await invite_to_assessment(
        email,
        "TEST-123",
    )

    if response["status"] == "success":
        candidate_repo.update(
            db,
            db_obj=candidate,
            obj_in={
                "hackerearth_assessment_url": response["assessment_url"]
            },
        )

    return response


# ============================================================
# AuthBridge Background Verification
# ============================================================

@router.post(
    "/authbridge/bgv/{candidate_id}",
    dependencies=[
        Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER]))
    ],
)
async def trigger_authbridge_bgv(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    candidate = candidate_repo.get(db, id=candidate_id)

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    candidate_data = {
        "name": candidate.name,
        "email": candidate.email,
    }

    response = await initiate_bgv(candidate_data)

    if response["status"] == "success":
        candidate_repo.update(
            db,
            db_obj=candidate,
            obj_in={
                "authbridge_bgv_status": response["bgv_status"]
            },
        )

    return response

