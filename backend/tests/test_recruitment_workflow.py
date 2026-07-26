import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import patch
from backend.database.models import UserRole
from backend.api.deps import get_current_user_role
from backend.main import app

@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user_role] = lambda: UserRole.RECRUITER
    yield
    app.dependency_overrides.pop(get_current_user_role, None)

def test_recruitment_workflow_empty_job_description(client: TestClient):
    for endpoint in ["/api/v1/recruitment/workflow", "/api/recruitment/workflow"]:
        response = client.post(
            endpoint,
            json={"candidate_id": 1, "job_description": "   "}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Job description cannot be empty."

def test_recruitment_workflow_candidate_not_found(client: TestClient):
    for endpoint in ["/api/v1/recruitment/workflow", "/api/recruitment/workflow"]:
        response = client.post(
            endpoint,
            json={"candidate_id": 999, "job_description": "Looking for a Python developer."}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Candidate not found."

@patch("backend.api.routes.candidate_repo.get")
def test_recruitment_workflow_no_resume(mock_get_candidate, client: TestClient):
    class MockCandidate:
        id = 1
        resume_path = None
        
    mock_get_candidate.return_value = MockCandidate()
    
    for endpoint in ["/api/v1/recruitment/workflow", "/api/recruitment/workflow"]:
        response = client.post(
            endpoint,
            json={"candidate_id": 1, "job_description": "We need a Senior Backend Dev."}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Candidate has no resume attached."

@patch("backend.api.routes.candidate_repo.get")
@patch("backend.api.routes.candidate_repo.update")
@patch("backend.api.routes.recruitment_workflow.invoke")
def test_recruitment_workflow_success(mock_invoke, mock_update_candidate, mock_get_candidate, client: TestClient):
    class MockCandidate:
        id = 1
        resume_path = "./uploads/test.pdf"
        
    mock_get_candidate.return_value = MockCandidate()
    
    mock_invoke.return_value = {
        "resume_path": "./uploads/test.pdf",
        "jd_text": "We need a Senior Backend Dev.",
        "resume_data": {
            "raw_text": "John Doe Resume. Experience: Google Senior Dev.",
            "experience": [{"company": "Google", "title": "Senior Dev"}],
            "education": [],
            "projects": [],
            "certifications": [],
            "current_company": "Google"
        },
        "extracted_skills": ["Python", "SQL"],
        "job_requirements": {"jd_keywords": ["Python", "SQL"]},
        "match_score": 85.0,
        "recommendation": "Strong Hire",
        "final_report": {
            "matched_skills": ["Python", "SQL"],
            "missing_skills": [],
            "score_breakdown": "{}"
        }
    }
    
    for endpoint in ["/api/v1/recruitment/workflow", "/api/recruitment/workflow"]:
        response = client.post(
            endpoint,
            json={"candidate_id": 1, "job_description": "We need a Senior Backend Dev."}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["match_score"] == 85.0
        assert data["recommendation"] == "Strong Hire"
        assert "Python" in data["skills"]
        assert mock_invoke.called
        assert mock_update_candidate.called
