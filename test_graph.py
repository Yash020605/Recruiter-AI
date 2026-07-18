import os
from backend.database.session import SessionLocal
from backend.database.models import Candidate
from backend.workflows.recruiter_graph import recruiter_graph
import logging

logging.basicConfig(level=logging.INFO)

db = SessionLocal()
candidate = db.query(Candidate).filter(Candidate.id == 3).first()
if candidate:
    initial_state = {
        "candidate_id": candidate.id,
        "resume_path": candidate.resume_path,
        "jd_text": "Looking for a React developer with Python skills.",
        "raw_resume_text": None,
        "skills": None,
        "experience": None,
        "education": None,
        "matched_skills": None,
        "missing_skills": None,
        "match_score": None,
        "recommendation": None,
        "messages": [],
        "chat_response": None
    }
    
    print("Invoking graph...")
    for step in recruiter_graph.stream(initial_state):
        print("STEP:", list(step.keys())[0])
else:
    print("Candidate not found.")
