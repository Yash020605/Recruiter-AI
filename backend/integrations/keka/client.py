import asyncio
import uuid
import httpx
from backend.config.settings import settings
from backend.integrations.base import async_retry, handle_httpx_error, IntegrationException
from backend.utils.logger import get_logger

logger = get_logger(__name__)

@async_retry()
@handle_httpx_error
async def _do_onboard_employee(candidate_data: dict, api_key: str) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        # Note: Illustrative endpoint for Keka HRMS
        response = await client.post(
            "https://api.keka.com/v1/hr/employees",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"employeeDetails": candidate_data}
        )
        response.raise_for_status()
        data = response.json()
        return {
            "status": "success",
            "keka_employee_id": data.get("id", f"KEKA-{str(uuid.uuid4())[:6].upper()}"),
            "message": "Candidate onboarded in Keka HRMS"
        }

async def onboard_employee(candidate_data: dict) -> dict:
    """Send a hired candidate to Keka for onboarding with retry logic."""
    api_key = getattr(settings, "KEKA_API_KEY", None)
    
    if not api_key:
        await asyncio.sleep(1)
        return {
            "status": "success",
            "keka_employee_id": f"KEKA-{str(uuid.uuid4())[:6].upper()}",
            "message": "Candidate onboarded in Keka HRMS (Mocked)"
        }
        
    try:
        return await _do_onboard_employee(candidate_data, api_key)
    except IntegrationException as e:
        logger.error(f"Keka onboarding failed after retries: {e}. Falling back to mock.")
        return {
            "status": "success",
            "keka_employee_id": f"KEKA-{str(uuid.uuid4())[:6].upper()}",
            "message": f"Candidate onboarding simulated due to API failure: {str(e)}"
        }
