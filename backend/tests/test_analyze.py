import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import patch
from backend.api.deps import get_current_user_role, get_current_user
from backend.database.models import UserRole
from backend.main import app

@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user_role] = lambda: UserRole.RECRUITER
    app.dependency_overrides[get_current_user] = lambda: "admin"
    yield
    app.dependency_overrides.pop(get_current_user_role, None)
    app.dependency_overrides.pop(get_current_user, None)

def test_analyze_empty_job_description(client: TestClient):
    response = client.post(
        "/api/v1/analyze",
        json={"candidate_id": 1, "job_description": "   "}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Job description cannot be empty."

def test_analyze_candidate_not_found(client: TestClient):
    response = client.post(
        "/api/v1/analyze",
        json={"candidate_id": 999, "job_description": "Looking for a Python developer."}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Candidate not found."

@patch("backend.api.routes.candidate_repo.get")
@patch("backend.api.routes.BackgroundTasks.add_task")
def test_analyze_success(mock_add_task, mock_get_candidate, client: TestClient):
    # Mock candidate record
    class MockCandidate:
        id = 1
        resume_path = "./uploads/test.pdf"
        
    mock_get_candidate.return_value = MockCandidate()
    
    response = client.post(
        "/api/v1/analyze",
        json={"candidate_id": 1, "job_description": "We need a Senior Backend Dev."}
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["status"] == "processing"
    assert mock_add_task.called
