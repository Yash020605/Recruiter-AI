import pytest
from fastapi.testclient import TestClient
from fastapi import status
import io

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
        files={"file": ("resume.docx", file_obj, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Only PDF and TXT files are supported."

def test_upload_empty_file(client: TestClient):
    file_content = b""
    file_obj = io.BytesIO(file_content)
    
    response = client.post(
        "/api/v1/upload",
        files={"file": ("resume.pdf", file_obj, "application/pdf")}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "The uploaded file is empty."
