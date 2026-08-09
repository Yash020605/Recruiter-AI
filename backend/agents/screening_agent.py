
import json
import time

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from backend.config.settings import settings
from backend.workflows.state import RecruiterState
from backend.utils.metrics import record_metric


# Primary LLM
primary_llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-4o-mini",
    api_key=settings.OPENAI_API_KEY
)

# Fallback LLM
fallback_llm = ChatOpenAI(
    temperature=0,
    model_name="nvidia/nemotron-3-ultra-550b-a55b",
    api_key=settings.NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

# Use primary LLM with fallback
llm = primary_llm.with_fallbacks([fallback_llm])


def extract_skills_node(state: RecruiterState) -> RecruiterState:
    """Extracts skills from raw resume text."""

    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Extract all technical and soft skills from the following resume text.

Return ONLY a JSON array of strings.

Resume:
{text}
"""
    )

    chain = prompt | llm

    start = time.time()
    response = chain.invoke({
        "text": state["raw_resume_text"]
    })

    record_metric(
        "llm_response_time",
        time.time() - start
    )

    try:
        content = response.content.strip()

        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]

        skills = json.loads(content)

        if not isinstance(skills, list):
            raise ValueError("Expected JSON array")

    except Exception as e:
        print(f"Error extracting skills: {e}")
        skills = []

    return {
        "skills": skills
    }


def extract_experience_node(state: RecruiterState) -> RecruiterState:
    """Extracts work experience from raw resume text."""

    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Extract work experience from the following resume text.

Return ONLY a JSON array of objects.

Each object must contain:
- "company"
- "title"
- "duration"
- "description"

Resume:
{text}
"""
    )

    chain = prompt | llm

    start = time.time()
    response = chain.invoke({
        "text": state["raw_resume_text"]
    })

    record_metric(
        "llm_response_time",
        time.time() - start
    )

    try:
        content = response.content.strip()

        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]

        experience = json.loads(content)

        if not isinstance(experience, list):
            raise ValueError("Expected JSON array")

    except Exception as e:
        print(f"Error extracting experience: {e}")
        experience = []

    return {
        "experience": experience
    }


def extract_education_node(state: RecruiterState) -> RecruiterState:
    """Extracts education details from raw resume text."""

    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Extract education history from the following resume text.

Return ONLY a JSON array of objects.

Each object must contain:
- "institution"
- "degree"
- "year"

Resume:
{text}
"""
    )

    chain = prompt | llm

    start = time.time()
    response = chain.invoke({
        "text": state["raw_resume_text"]
    })

    record_metric(
        "llm_response_time",
        time.time() - start
    )

    try:
        content = response.content.strip()

        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]

        education = json.loads(content)

        if not isinstance(education, list):
            raise ValueError("Expected JSON array")

    except Exception as e:
        print(f"Error extracting education: {e}")
        education = []

    return {
        "education": education
    }


def extract_recruitment_details_node(state: RecruiterState) -> dict:
    """
    Extracts and normalizes advanced recruitment details
    from raw resume text.

    New features:
    - Current CTC extraction
    - Expected CTC extraction
    - Current CTC normalization to LPA
    - Expected CTC normalization to LPA
    - Notice period extraction
    - Notice period normalization to days
    - Immediate joiner detection
    - Preferred location extraction
    """

    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Extract recruitment-related details from the candidate's resume text.

Return ONLY a valid JSON object with the following keys.

Use null when information is not available.

IMPORTANT RULES:

1. Preserve the original salary text in current_ctc and expected_ctc.
2. Normalize salary values to annual LPA when possible.
3. Normalize notice period to number of days.
4. If the candidate can join immediately, set immediate_joiner to "Yes".
5. If the candidate has a notice period, set immediate_joiner to "No".
6. If immediate joining cannot be determined, use null.
7. Do not guess information that is not present in the resume.

FIELDS:

- "current_company": string or null

- "current_ctc": string or null
  Examples:
  "12 LPA"
  "₹12 LPA"
  "12 lakhs"
  "$100k"

- "current_ctc_lpa": number or null

- "expected_ctc": string or null
  Examples:
  "15 LPA"
  "₹15 LPA"
  "15 lakhs"

- "expected_ctc_lpa": number or null

- "notice_period": string or null
  Examples:
  "30 days"
  "2 months"
  "60 days"
  "Immediate"
  "15 days"

- "notice_period_days": integer or null

  Conversion examples:
  "Immediate" = 0
  "15 days" = 15
  "30 days" = 30
  "2 months" = approximately 60
  "3 months" = approximately 90

- "immediate_joiner": string or null

  Use:
  "Yes" = candidate explicitly says they can join immediately
  "No" = candidate explicitly indicates a notice period
  null = cannot be determined

- "preferred_location": string or null

Resume:
{text}
"""
    )

    chain = prompt | llm

    start = time.time()

    response = chain.invoke({
        "text": state["raw_resume_text"]
    })

    record_metric(
        "llm_response_time",
        time.time() - start
    )

    try:
        content = response.content.strip()

        # Remove Markdown JSON code fences if returned by LLM
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]

        content = content.strip()

        data = json.loads(content)

        if not isinstance(data, dict):
            raise ValueError("Expected JSON object")

    except Exception as e:
        print(f"Error extracting recruitment details: {e}")
        data = {}

    return {
        "current_company": data.get("current_company"),

        # Original values
        "current_ctc": data.get("current_ctc"),
        "expected_ctc": data.get("expected_ctc"),
        "notice_period": data.get("notice_period"),

        # Normalized values
        "current_ctc_lpa": data.get("current_ctc_lpa"),
        "expected_ctc_lpa": data.get("expected_ctc_lpa"),
        "notice_period_days": data.get("notice_period_days"),

        # Immediate joining
        "immediate_joiner": data.get("immediate_joiner"),

        # Location
        "preferred_location": data.get("preferred_location")
    }


def extract_projects_and_certs_node(state: RecruiterState) -> dict:
    """Extracts projects and certifications from raw resume text."""

    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Extract projects and certifications from the following resume text.

Return ONLY a valid JSON object with two keys:

- "projects": array of objects, where each object has:
  - "title"
  - "description"

- "certifications": array of strings

Resume:
{text}
"""
    )

    chain = prompt | llm

    start = time.time()

    response = chain.invoke({
        "text": state["raw_resume_text"]
    })

    record_metric(
        "llm_response_time",
        time.time() - start
    )

    try:
        content = response.content.strip()

        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]

        content = content.strip()

        data = json.loads(content)

        if not isinstance(data, dict):
            raise ValueError("Expected JSON object")

    except Exception as e:
        print(f"Error extracting projects/certifications: {e}")
        data = {}

    return {
        "projects": data.get("projects", []),
        "certifications": data.get("certifications", [])
    }

