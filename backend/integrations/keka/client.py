import asyncio
import uuid
from backend.config.settings import settings

async def onboard_employee(candidate_data: dict) -> dict:
    """Mock sending a hired candidate to Keka for onboarding."""
    await asyncio.sleep(1)
    return {
        "status": "success",
        "keka_employee_id": f"KEKA-{str(uuid.uuid4())[:6].upper()}",
        "message": "Candidate onboarded in Keka HRMS"
    }
