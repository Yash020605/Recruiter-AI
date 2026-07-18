import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

class APIClient:
    def __init__(self):
        self.base_url = API_URL
        
    def _get_headers(self):
        headers = {}
        token = st.session_state.get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/login",
            data={"username": username, "password": password}
        )
        return response

    def upload_resume(self, file_bytes, filename):
        files = {"file": (filename, file_bytes, "application/pdf")}
        response = requests.post(
            f"{self.base_url}/upload",
            files=files,
            headers=self._get_headers()
        )
        return response

    def trigger_analysis(self, candidate_id, jd):
        response = requests.post(
            f"{self.base_url}/analyze",
            json={"candidate_id": candidate_id, "job_description": jd},
            headers=self._get_headers()
        )
        return response

    def get_candidates(self):
        response = requests.get(
            f"{self.base_url}/candidates",
            headers=self._get_headers()
        )
        return response

    def chat_with_agent(self, candidate_id, message):
        response = requests.post(
            f"{self.base_url}/chat",
            json={"candidate_id": candidate_id, "message": message},
            headers=self._get_headers()
        )
        return response
        
api_client = APIClient()
