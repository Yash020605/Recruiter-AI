from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from backend.config.settings import settings

llm = ChatGoogleGenerativeAI(
    google_api_key=settings.GEMINI_API_KEY,
    model="gemini-1.5-flash",
    temperature=0.7
)

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
