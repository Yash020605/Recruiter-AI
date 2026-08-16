import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from backend.config.settings import settings

llm = ChatGoogleGenerativeAI(
    google_api_key=settings.GEMINI_API_KEY,
    model="gemini-1.5-flash",
    temperature=0
)

def extract_keywords_from_text(text: str) -> list:
    """Extracts a list of key technical skills from text (like a JD)."""
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Extract the core technical skills and requirements from the following text.
Return ONLY a JSON array of strings. Do not include any other text.
Text: {text}
"""
    )
    
    chain = prompt | llm
    response = chain.invoke({"text": text})
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        return json.loads(content)
    except Exception:
        return []
