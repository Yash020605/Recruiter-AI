from langgraph.graph import StateGraph, END
from backend.workflows.state import RecruiterState

from backend.agents.jd_agent import jd_agent_node
from backend.agents.resume_agent import resume_agent_node
from backend.agents.evaluation_agent import evaluation_agent_node
from backend.agents.recommendation_agent import recommendation_agent_node
from backend.agents.database_agent import database_agent_node

def supervisor_node(state: RecruiterState) -> RecruiterState:
    """Recruiter Supervisor Agent: Entry point, routes to JD and Resume agents."""
    return {}

def build_recruiter_graph():
    workflow = StateGraph(RecruiterState)
    
    # Add nodes (The new Agentic architecture)
    workflow.add_node("supervisor_agent", supervisor_node)
    workflow.add_node("jd_agent", jd_agent_node)
    workflow.add_node("resume_agent", resume_agent_node)
    workflow.add_node("evaluation_agent", evaluation_agent_node)
    workflow.add_node("recommendation_agent", recommendation_agent_node)
    workflow.add_node("database_agent", database_agent_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor_agent")
    
    # Fan-out: Supervisor -> Resume, JD, DB
    workflow.add_edge("supervisor_agent", "resume_agent")
    workflow.add_edge("supervisor_agent", "jd_agent")
    workflow.add_edge("supervisor_agent", "database_agent")
    
    # Fan-in: Resume, JD, DB -> Evaluation
    workflow.add_edge("resume_agent", "evaluation_agent")
    workflow.add_edge("jd_agent", "evaluation_agent")
    workflow.add_edge("database_agent", "evaluation_agent")
    
    # Evaluation -> Recommendation -> END
    workflow.add_edge("evaluation_agent", "recommendation_agent")
    workflow.add_edge("recommendation_agent", END)
    
    return workflow.compile()

recruiter_graph = build_recruiter_graph()
