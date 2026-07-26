from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from backend.config.settings import settings

primary_llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)
fallback_llm = ChatOpenAI(
    temperature=0.7, 
    model_name="nvidia/nemotron-3-ultra-550b-a55b", 
    api_key=settings.NVIDIA_API_KEY, 
    base_url="https://integrate.api.nvidia.com/v1"
)
llm = primary_llm.with_fallbacks([fallback_llm])

def generate_communication_template(candidate_data: dict, email_type: str) -> str:
    """
    Generates a personalized communication template based on candidate data and requested email type.
    email_type can be: "invite", "reject", "offer"
    """
    
    if email_type == "invite":
        context_prompt = "The candidate has been shortlisted. Draft a polite and professional interview invitation email."
    elif email_type == "reject":
        context_prompt = "The candidate was not a fit for this role. Draft a polite and professional rejection email."
    elif email_type == "offer":
        context_prompt = "The candidate has passed all interviews. Draft an enthusiastic job offer email."
    else:
        context_prompt = "Draft a professional update email regarding their application status."

    prompt = PromptTemplate(
        input_variables=["name", "score", "matched", "missing", "context"],
        template="""You are an AI HR Assistant generating an email template for a candidate.

Candidate Name: {name}
Match Score: {score}/100
Matched Skills: {matched}
Missing Skills: {missing}

Task: {context}

Generate the email body. Make it professional, empathetic, and clear. Leave placeholders like [Company Name], [Date], etc. where appropriate.
Return ONLY the email content.
"""
    )
    
    chain = prompt | llm
    
    response = chain.invoke({
        "name": candidate_data.get("name", "Candidate"),
        "score": candidate_data.get("score", 0.0),
        "matched": ", ".join(candidate_data.get("matched_skills", [])),
        "missing": ", ".join(candidate_data.get("missing_skills", [])),
        "context": context_prompt
    })
    
    return response.content.strip()
