import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def get_auth_headers():
    response = client.post(
        "/api/v1/login",
        data={"username": "recruiter", "password": "recruiter"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}

def test_add_and_search_sourced_candidate():
    headers = get_auth_headers()

    # 1. Add Sourced Candidate from GitHub
    payload = {
        "name": "Sarah Developer",
        "email": "sarah.dev@example.com",
        "phone": "+1234567890",
        "current_company": "Tech Corp",
        "preferred_location": "Remote",
        "skills": "Python, FastAPI, TypeScript, React, Docker",
        "experience": "5 years as Senior Software Engineer",
        "education": "BS in Computer Science",
        "source_platform": "GitHub",
        "source_url": "https://github.com/octocat",
        "recruiter": "Recruiter Alice",
        "initial_notes": "Sourced from top Python contributors list.",
        "social_profiles": [
            {
                "platform": "GitHub",
                "profile_url": "https://github.com/octocat",
                "username": "octocat",
                "bio": "The Octocat developer",
                "location": "San Francisco",
                "skills": "Git, C, Python",
                "followers": 1500,
                "repositories_count": 8,
                "top_languages": "C, Python",
                "total_stars": 320
            }
        ]
    }
    response = client.post("/api/v1/sourcing/candidates", json=payload, headers=headers)
    assert response.status_code == 201
    candidate = response.json()
    candidate_id = candidate["id"]
    assert candidate["name"] == "Sarah Developer"
    assert len(candidate["sources"]) >= 1
    assert len(candidate["social_profiles"]) >= 1

    # 2. Add LinkedIn Profile manually
    profile_payload = {
        "platform": "LinkedIn",
        "profile_url": "https://linkedin.com/in/sarah-developer",
        "bio": "Senior Backend Architect with Python expertise.",
        "location": "San Francisco",
        "skills": "Python, System Design"
    }
    sp_resp = client.post(f"/api/v1/sourcing/candidates/{candidate_id}/social-profile", json=profile_payload, headers=headers)
    assert sp_resp.status_code == 200
    assert sp_resp.json()["platform"] == "LinkedIn"

    # 3. Filter Sourced Candidates
    search_resp = client.get("/api/v1/sourcing/candidates?source_platform=GitHub&skills=Python", headers=headers)
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) >= 1
    assert any(c["id"] == candidate_id for c in results)

    # 4. Move Candidate through Sourcing Pipeline
    pipeline_resp = client.put(f"/api/v1/sourcing/candidates/{candidate_id}/pipeline", json={
        "stage": "Contacted",
        "notes": "Sent outreach email via LinkedIn."
    }, headers=headers)
    assert pipeline_resp.status_code == 200
    assert pipeline_resp.json()["stage"] == "Contacted"

    # Move to Interested
    pipeline_resp2 = client.put(f"/api/v1/sourcing/candidates/{candidate_id}/pipeline", json={
        "stage": "Interested",
        "notes": "Candidate replied expressing interest!"
    }, headers=headers)
    assert pipeline_resp2.status_code == 200
    assert pipeline_resp2.json()["stage"] == "Interested"

    # 5. Get Candidate Sourcing History
    history_resp = client.get(f"/api/v1/sourcing/candidates/{candidate_id}/history", headers=headers)
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert len(history["pipeline_history"]) >= 2

    # 6. Rank Sourced Candidate using existing AI matching logic
    rank_resp = client.post(f"/api/v1/sourcing/candidates/{candidate_id}/rank", json={
        "job_description": "We are seeking a Senior Python Architect skilled in FastAPI, System Design, and Microservices."
    }, headers=headers)
    assert rank_resp.status_code == 200
    rank_data = rank_resp.json()
    assert rank_data["status"] == "success"
    assert rank_data["match_score"] > 0
