from backend.workflows.state import RecruiterState

def assistant_agent_node(state: RecruiterState) -> RecruiterState:
    """Recruiter Assistant Agent: Formulates final response/summary."""
    score = state.get("match_score", 0)
    name = state.get("candidate_id", "Unknown")
    
    if score > 75:
        reply = f"Candidate {name} looks like a strong match ({score}%)."
    else:
        reply = f"Candidate {name} might need more review ({score}%)."
        
    return {"chat_response": reply}
