import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import patch

def test_login_success(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrong", "password": "wrong"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"
