import pytest
from fastapi.testclient import TestClient
from fastapi import status
import io
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

def test_upload_valid_pdf(client: TestClient):
    file_content = b"%PDF-1.4 Mock PDF Content"
    file_obj = io.BytesIO(file_content)
    
    response = client.post(
        "/api/v1/upload",
        files={"file": ("resume.pdf", file_obj, "application/pdf")}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["name"] == "Pending Extraction"
    assert data["resume_path"].endswith(".pdf")

def test_upload_invalid_extension(client: TestClient):
    file_content = b"Some content"
    file_obj = io.BytesIO(file_content)
    
    response = client.post(
        "/api/v1/upload",
        files={"file": ("resume.zip", file_obj, "application/zip")}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Only PDF, DOCX and TXT files are supported."

def test_upload_empty_file(client: TestClient):
    file_content = b""
    file_obj = io.BytesIO(file_content)
    
    response = client.post(
        "/api/v1/upload",
        files={"file": ("resume.pdf", file_obj, "application/pdf")}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "The uploaded file is empty."
