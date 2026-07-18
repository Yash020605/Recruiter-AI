import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

nvidia_api_key = os.getenv("NVIDIA_API_KEY")

fallback_llm = ChatOpenAI(
    temperature=0, 
    model_name="nvidia/nemotron-4-340b-instruct", 
    api_key=nvidia_api_key, 
    base_url="https://integrate.api.nvidia.com/v1"
)

try:
    print("Invoking NVIDIA LLM...")
    response = fallback_llm.invoke("Hello, who are you?")
    print("Response:", response.content)
except Exception as e:
    print("Error:", repr(e))
