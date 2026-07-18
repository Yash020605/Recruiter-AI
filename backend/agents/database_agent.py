import json
from backend.workflows.state import RecruiterState
from backend.tools.candidate_database import candidate_repo
from backend.database.postgres import SessionLocal

def database_agent_node(state: RecruiterState) -> RecruiterState:
    """Candidate Database Agent: Fetches historical context about the candidate from PostgreSQL."""
    db = SessionLocal()
    try:
        cid = state.get("candidate_id")
        if cid:
            candidate = candidate_repo.get(db, id=cid)
            # Future expansion: load historical applications, previous scores, or cross-reference 
            # with other open roles. For now, it satisfies the parallel fan-out architecture.
    finally:
        db.close()
    return {}
