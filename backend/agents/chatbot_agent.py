from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, SystemMessage
from backend.utils.llm import get_llm
from backend.tools.candidate_database import candidate_repo
from backend.utils.logger import get_logger

logger = get_logger(__name__)

def query_global_candidates(message: str, db: Session) -> str:
    """Answers user queries about the candidates in the database."""
    # 1. Fetch all candidates
    candidates = candidate_repo.get_all(db, limit=100) # limit to 100 to avoid huge context in MVP
    
    # 2. Format candidates into text
    if not candidates:
        candidate_context = "The database is currently empty. There are no candidates."
    else:
        candidate_lines = []
        for c in candidates:
            # We provide basic details that a recruiter might ask about
            info = (f"- ID: {c.id} | Name: {c.name or 'Unknown'} | Email: {c.email or 'N/A'} "
                    f"| Phone: {c.phone or 'N/A'} | Status: {c.status} | Match Score: {c.match_score or 'N/A'}")
            
            # Optionally add skills if analyzed
            if c.matched_skills and len(c.matched_skills) > 2: # more than "[]"
                info += f" | Matched Skills: {c.matched_skills}"
            if c.recommendation:
                rec_snippet = c.recommendation.split(":")[0] if ":" in c.recommendation else c.recommendation
                info += f" | Rec: {rec_snippet}"
                
            candidate_lines.append(info)
        
        candidate_context = "Current Candidates in Database:\n" + "\n".join(candidate_lines)
    
    # 3. Create prompt
    system_prompt = (
        "You are an AI Recruiter Assistant. Your job is to answer the user's questions about the candidates in the database.\n"
        "Use ONLY the following context to answer the question. If the answer is not in the context, say 'I don't have that information'.\n"
        "Be concise and professional.\n\n"
        f"{candidate_context}"
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=message)
    ]
    
    # 4. Query LLM
    try:
        llm = get_llm()
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        logger.error(f"Chatbot Error: {str(e)}")
        return "I'm sorry, I encountered an error while processing your request."

def query_candidate(message: str, candidate_id: int, db: Session) -> str:
    """Answers user queries about a specific candidate in the database."""
    # 1. Fetch the candidate
    candidate = candidate_repo.get(db, id=candidate_id)
    if not candidate:
        return "I'm sorry, I couldn't find that candidate in the database."
    
    # 2. Format candidate into text
    info = (f"Candidate Details:\n"
            f"- Name: {candidate.name or 'Unknown'}\n"
            f"- Email: {candidate.email or 'N/A'}\n"
            f"- Phone: {candidate.phone or 'N/A'}\n"
            f"- Current Company: {candidate.current_company or 'N/A'}\n"
            f"- Current CTC: {candidate.current_ctc or 'N/A'}\n"
            f"- Expected CTC: {candidate.expected_ctc or 'N/A'}\n"
            f"- Notice Period: {candidate.notice_period or 'N/A'}\n"
            f"- Preferred Location: {candidate.preferred_location or 'N/A'}\n"
            f"- Status: {candidate.status}\n"
            f"- Match Score: {candidate.match_score or 'N/A'}\n"
            f"- Recommendation: {candidate.recommendation or 'N/A'}\n"
            f"- Skills: {candidate.skills or 'N/A'}\n"
            f"- Matched Skills: {candidate.matched_skills or 'N/A'}\n"
            f"- Missing Skills: {candidate.missing_skills or 'N/A'}\n"
            f"- Experience: {candidate.experience or 'N/A'}\n"
            f"- Education: {candidate.education or 'N/A'}\n"
            f"- Projects: {candidate.projects or 'N/A'}\n"
            f"- Certifications: {candidate.certifications or 'N/A'}\n")
    
    # 3. Create prompt
    system_prompt = (
        "You are an AI Recruiter Assistant. Your job is to answer the user's questions about a specific candidate.\n"
        "Use ONLY the following context to answer the question. If the answer is not in the context, say 'I don't have that information'.\n"
        "Be concise and professional.\n\n"
        f"{info}"
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=message)
    ]
    
    # 4. Query LLM
    try:
        llm = get_llm()
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        logger.error(f"Chatbot Error: {str(e)}")
        return "I'm sorry, I encountered an error while processing your request."

