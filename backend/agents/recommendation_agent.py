import time
from langchain_core.prompts import PromptTemplate
from backend.workflows.state import RecruiterState
from backend.agents.screening_agent import llm
from backend.utils.metrics import record_metric

def recommendation_agent_node(state: RecruiterState) -> RecruiterState:
    """Recommendation Agent: Generates a final hiring recommendation."""
    score = state.get("match_score", 0)
    breakdown = state.get("score_breakdown", "{}")
    jd = state.get("jd_text", "")
    
    prompt = PromptTemplate(
        input_variables=["score", "breakdown", "jd"],
        template="""You are a senior technical recruiter. 
Based on the candidate's Match Score ({score}/100) and the Score Breakdown ({breakdown}), provide a final recommendation for the following Job Description:
{jd}

Return exactly one of: "Strong Hire", "Hire", "Consider", or "Reject" followed by a short one-sentence justification.
Example: "Strong Hire: Excellent skills and experience match for this role."
"""
    )
    chain = prompt | llm
    
    try:
        start = time.time()
        response = chain.invoke({
            "score": score,
            "breakdown": breakdown,
            "jd": jd
        })
        record_metric("llm_response_time", time.time() - start)
        rec = response.content.strip()
    except Exception as e:
        print(f"Error in recommendation LLM: {e}")
        if score >= 90:
            rec = "Strong Hire: Automatic fallback based on exceptionally high score."
        elif score >= 75:
            rec = "Hire: Automatic fallback based on strong score."
        elif score >= 50:
            rec = "Consider: Automatic fallback based on average score."
        else:
            rec = "Reject: Automatic fallback based on low score."
            
    return {"recommendation": rec}
