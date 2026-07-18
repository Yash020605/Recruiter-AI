import asyncio
import random
from backend.config.settings import settings

async def initiate_bgv(candidate_data: dict) -> dict:
    """Mock initiating background verification via AuthBridge."""
    await asyncio.sleep(1)
    return {
        "status": "success",
        "bgv_status": "Pending",
        "message": "Background verification initiated via AuthBridge"
    }

async def poll_bgv_status(candidate_id: str) -> dict:
    """Mock polling AuthBridge for updated BGV status."""
    await asyncio.sleep(1)
    statuses = ["Pending", "Clear", "Discrepancy"]
    return {
        "status": "success",
        "bgv_status": random.choice(statuses),
        "message": "Polled latest BGV status"
    }
