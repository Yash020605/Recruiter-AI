from fastapi.testclient import TestClient
from fastapi import status

def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "AI Recruiter Assistant API is running"}
