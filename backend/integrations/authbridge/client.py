import asyncio
import random
import httpx
from backend.config.settings import settings
from backend.integrations.base import async_retry, handle_httpx_error, IntegrationException
from backend.utils.logger import get_logger

logger = get_logger(__name__)

@async_retry()
@handle_httpx_error
async def _do_initiate_bgv(candidate_data: dict, api_key: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Note: Illustrative endpoint for AuthBridge BGV
        response = await client.post(
            "https://api.authbridge.com/v1/bgv/initiate",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"candidate": candidate_data}
        )
        response.raise_for_status()
        data = response.json()
        return {
            "status": "success",
            "bgv_status": data.get("status", "Pending"),
            "message": "Background verification initiated via AuthBridge"
        }

async def initiate_bgv(candidate_data: dict) -> dict:
    """Initiate background verification via AuthBridge with retries."""
    api_key = getattr(settings, "AUTHBRIDGE_API_KEY", None)
    
    if not api_key:
        await asyncio.sleep(1)
        return {
            "status": "success",
            "bgv_status": "Pending",
            "message": "Background verification initiated via AuthBridge (Mocked)"
        }
        
    try:
        return await _do_initiate_bgv(candidate_data, api_key)
    except IntegrationException as e:
        logger.error(f"AuthBridge initiate BGV failed after retries: {e}. Falling back to mock.")
        return {
            "status": "success",
            "bgv_status": "Pending",
            "message": f"BGV initiated simulated due to API failure: {str(e)}"
        }

@async_retry()
@handle_httpx_error
async def _do_poll_bgv_status(candidate_id: str, api_key: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"https://api.authbridge.com/v1/bgv/status/{candidate_id}",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        response.raise_for_status()
        data = response.json()
        return {
            "status": "success",
            "bgv_status": data.get("status", "Clear"),
            "message": "Polled latest BGV status"
        }

async def poll_bgv_status(candidate_id: str) -> dict:
    """Poll AuthBridge for updated BGV status with retries."""
    api_key = getattr(settings, "AUTHBRIDGE_API_KEY", None)
    
    if not api_key:
        await asyncio.sleep(1)
        statuses = ["Pending", "Clear", "Discrepancy"]
        return {
            "status": "success",
            "bgv_status": random.choice(statuses),
            "message": "Polled latest BGV status (Mocked)"
        }
        
    try:
        return await _do_poll_bgv_status(candidate_id, api_key)
    except IntegrationException as e:
        logger.error(f"AuthBridge poll status failed after retries: {e}. Falling back to mock.")
        statuses = ["Pending", "Clear", "Discrepancy"]
        return {
            "status": "success",
            "bgv_status": random.choice(statuses),
            "message": f"Polled status simulated due to API failure: {str(e)}"
        }
