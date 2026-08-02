import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session
from backend.database.models import Candidate, UserRole, CandidateJourney
from backend.api.deps import get_current_user_role, get_current_user
from backend.main import app

@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user_role] = lambda: UserRole.RECRUITER
    app.dependency_overrides[get_current_user] = lambda: "admin"
    yield
    app.dependency_overrides.pop(get_current_user_role, None)
    app.dependency_overrides.pop(get_current_user, None)

@pytest.fixture
def create_test_candidate(db_session: Session):
    candidate = Candidate(
        name="Test Candidate",
        resume_path="./uploads/test.pdf",
        status="Applied",
        gender="Female",
        total_experience_years=3.5,
        highest_education_level="Masters",
        preferred_location="New York"
    )
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)
    
    # Log initial event
    journey = CandidateJourney(
        candidate_id=candidate.id,
        stage="Applied",
        status="Completed",
        remarks="Candidate profile created.",
        updated_by="System"
    )
    db_session.add(journey)
    db_session.commit()
    
    return candidate

def test_get_journey_history(client: TestClient, create_test_candidate):
    candidate = create_test_candidate
    response = client.get(f"/api/v1/candidates/{candidate.id}/journey")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["stage"] == "Applied"
    assert data[0]["status"] == "Completed"
    assert data[0]["remarks"] == "Candidate profile created."

def test_add_journey_event(client: TestClient, create_test_candidate, db_session: Session):
    candidate = create_test_candidate
    response = client.post(
        f"/api/v1/candidates/{candidate.id}/journey",
        json={
            "stage": "Shortlisted",
            "status": "Completed",
            "remarks": "Strong technical skills.",
            "updated_by": "admin"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["stage"] == "Shortlisted"
    assert data["status"] == "Completed"
    assert data["remarks"] == "Strong technical skills."
    
    # Check if candidate status is updated
    db_session.refresh(candidate)
    assert candidate.status == "Shortlisted"

def test_update_candidate_status_logs_journey(client: TestClient, create_test_candidate, db_session: Session):
    candidate = create_test_candidate
    # Update candidate status via PUT endpoint
    response = client.put(
        f"/api/v1/candidates/{candidate.id}",
        json={"status": "Interview Scheduled"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Check if a journey event was automatically logged
    journeys = db_session.query(CandidateJourney).filter(
        CandidateJourney.candidate_id == candidate.id
    ).order_by(CandidateJourney.created_at.asc()).all()
    
    assert len(journeys) == 2
    assert journeys[1].stage == "Interview Scheduled"
    assert "transitioned" in journeys[1].remarks

def test_get_diversity_analytics(client: TestClient, create_test_candidate):
    response = client.get("/api/v1/analytics/diversity")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "gender_distribution" in data
    assert "education_distribution" in data
    assert "experience_distribution" in data
    assert "location_distribution" in data
    assert "hiring_funnel" in data
    assert data["selection_rate"] == 0.0 # because status is Applied (or not Hired)
    assert data["rejection_rate"] == 0.0
    
    # Check gender distribution values
    gender_dist = {item["name"]: item["value"] for item in data["gender_distribution"]}
    assert gender_dist["Female"] == 1
