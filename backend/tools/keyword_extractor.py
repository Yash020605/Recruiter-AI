import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from backend.config.settings import settings

primary_llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)
fallback_llm = ChatOpenAI(
    temperature=0, 
    model_name="nvidia/nemotron-3-ultra-550b-a55b", 
    api_key=settings.NVIDIA_API_KEY, 
    base_url="https://integrate.api.nvidia.com/v1"
)
llm = primary_llm.with_fallbacks([fallback_llm])

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
