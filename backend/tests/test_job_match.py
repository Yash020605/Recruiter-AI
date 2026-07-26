import json
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
from backend.database.models import Candidate, UserRole
from backend.api.deps import get_current_user_role
from backend.main import app

@pytest.fixture(autouse=True)
def override_auth():
    # Override auth to allow all requests to proceed with RECRUITER role
    app.dependency_overrides[get_current_user_role] = lambda: UserRole.RECRUITER
    yield
    app.dependency_overrides.pop(get_current_user_role, None)

def test_job_match_candidate_not_found(client: TestClient):
    response = client.post(
        "/api/v1/job/match",
        json={"candidate_id": 999, "job_description": "We need a Python developer."}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Candidate not found."

def test_job_match_empty_job_description(client: TestClient):
    response = client.post(
        "/api/v1/job/match",
        json={"candidate_id": 1, "job_description": "   "}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Job description cannot be empty."

@patch("langchain_openai.ChatOpenAI.invoke")
def test_job_match_success(mock_invoke, client: TestClient, db_session: Session):
    # 1. Create a candidate with parsed skills and save to DB
    candidate = Candidate(
        name="John Doe",
        resume_path="./uploads/test_resume.pdf",
        skills=json.dumps(["Python", "FastAPI", "SQL"]),
        experience=json.dumps([{"company": "A", "title": "Developer", "duration": "2 years", "description": ""}]),
        education=json.dumps([{"institution": "B", "degree": "BS", "year": "2020"}]),
        projects=json.dumps([]),
        certifications=json.dumps([])
    )
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)

    # 2. Setup mock LLM responses
    mock_jd_res = MagicMock()
    mock_jd_res.content = json.dumps({
        "technical_skills": ["Python", "React"],
        "soft_skills": ["Communication"],
        "experience": "2+ years",
        "education": "BS",
        "certifications": []
    })

    mock_match_res = MagicMock()
    mock_match_res.content = json.dumps({
        "match_score": 85.0,
        "matched_skills": ["Python"],
        "missing_skills": ["React"],
        "extra_skills": ["FastAPI", "SQL"],
        "summary": "Great Python developer with extra backend experience."
    })

    mock_invoke.side_effect = [mock_jd_res, mock_match_res]

    # 3. Call the match API
    response = client.post(
        "/api/v1/job/match",
        json={"candidate_id": candidate.id, "job_description": "Looking for a Python and React developer."}
    )

    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()
    assert res_data["match_score"] == 85.0
    assert "Python" in res_data["matched_skills"]
    assert "React" in res_data["missing_skills"]
    assert "FastAPI" in res_data["extra_skills"]
    assert res_data["summary"] == "Great Python developer with extra backend experience."
