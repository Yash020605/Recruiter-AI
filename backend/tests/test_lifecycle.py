import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def get_auth_headers():
    # Attempt login or generate mock token
    response = client.post(
        "/api/v1/login",
        data={"username": "recruiter", "password": "recruiter"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}

def test_job_and_stage_lifecycle():
    headers = get_auth_headers()
    # 1. Create a job
    job_payload = {
        "title": "Senior AI Architect",
        "department": "Engineering",
        "location": "San Francisco, CA",
        "description": "Lead multi-agent AI framework deployment.",
        "requirements": "Python, LangGraph, FastAPI, PostgreSQL",
        "status": "Active"
    }
    response = client.post("/api/v1/jobs", json=job_payload, headers=headers)
    assert response.status_code == 201
    job = response.json()
    job_id = job["id"]
    assert job["title"] == "Senior AI Architect"
    assert len(job["stages"]) >= 5

    # 2. Add custom stage
    stage_payload = {
        "name": "Architecture Review",
        "stage_order": 3,
        "is_default": False
    }
    stage_resp = client.post(f"/api/v1/jobs/{job_id}/stages", json=stage_payload, headers=headers)
    assert stage_resp.status_code == 200
    assert stage_resp.json()["name"] == "Architecture Review"

    # 3. List jobs
    jobs_resp = client.get("/api/v1/jobs", headers=headers)
    assert jobs_resp.status_code == 200
    assert len(jobs_resp.json()) >= 1

def test_application_interview_offer_onboarding_lifecycle():
    headers = get_auth_headers()

    # Create candidate
    cand_resp = client.post(
        "/api/v1/upload",
        files={"file": ("test_cv.txt", b"Skills: Python, FastAPI, React", "text/plain")},
        headers=headers
    )
    assert cand_resp.status_code == 201
    candidate_id = cand_resp.json()["id"]

    # 1. Create Application
    app_payload = {
        "candidate_id": candidate_id,
        "source": "LinkedIn",
        "stage_name": "Screening",
        "status": "In Progress"
    }
    app_resp = client.post("/api/v1/applications", json=app_payload, headers=headers)
    assert app_resp.status_code == 201
    app_id = app_resp.json()["id"]

    # 2. Schedule Interview
    interview_payload = {
        "candidate_id": candidate_id,
        "application_id": app_id,
        "interviewer": "Tech Lead John",
        "scheduled_at": (datetime.now() + timedelta(days=2)).isoformat(),
        "interview_type": "System Design",
        "status": "Scheduled",
        "meeting_link": "https://meet.google.com/abc-defg-hij"
    }
    int_resp = client.post("/api/v1/interviews", json=interview_payload, headers=headers)
    assert int_resp.status_code == 201
    interview_id = int_resp.json()["id"]

    # Add Feedback
    fb_payload = {
        "interviewer": "Tech Lead John",
        "feedback": "Outstanding architectural knowledge.",
        "rating": 4.8,
        "recommendation": "Strong Hire"
    }
    fb_resp = client.post(f"/api/v1/interviews/{interview_id}/feedback", json=fb_payload, headers=headers)
    assert fb_resp.status_code == 200
    assert fb_resp.json()["rating"] == 4.8

    # 3. Create Assessment Result
    ass_resp = client.post("/api/v1/assessments", json={"title": "Python Core", "max_score": 100}, headers=headers)
    assert ass_resp.status_code == 201
    assessment_id = ass_resp.json()["id"]

    result_resp = client.post("/api/v1/assessment-results", json={
        "assessment_id": assessment_id,
        "candidate_id": candidate_id,
        "application_id": app_id,
        "score": 92.5,
        "result": "Pass",
        "feedback": "Passed all edge cases"
    }, headers=headers)
    assert result_resp.status_code == 201

    # 4. Create & Accept Offer
    offer_resp = client.post("/api/v1/offers", json={
        "candidate_id": candidate_id,
        "application_id": app_id,
        "salary": 140000.0,
        "currency": "USD",
        "status": "Sent"
    }, headers=headers)
    assert offer_resp.status_code == 201
    offer_id = offer_resp.json()["id"]

    update_offer_resp = client.put(f"/api/v1/offers/{offer_id}", json={"status": "Accepted"}, headers=headers)
    assert update_offer_resp.status_code == 200
    assert update_offer_resp.json()["status"] == "Accepted"

    # 5. Initiate Onboarding
    onboard_resp = client.post("/api/v1/onboarding", json={
        "candidate_id": candidate_id,
        "application_id": app_id,
        "joining_status": "In Progress",
        "document_verification": "Verified",
        "background_check_status": "Passed"
    }, headers=headers)
    assert onboard_resp.status_code == 201
    assert onboard_resp.json()["joining_status"] == "In Progress"

    # 6. Check Activity Logs
    logs_resp = client.get(f"/api/v1/activity-logs?candidate_id={candidate_id}", headers=headers)
    assert logs_resp.status_code == 200
    assert len(logs_resp.json()) >= 3
