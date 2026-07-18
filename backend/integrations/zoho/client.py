import asyncio
import uuid
from backend.config.settings import settings

async def sync_candidate_to_ats(candidate_data: dict) -> dict:
    """Mock syncing candidate data to Zoho ATS."""
    await asyncio.sleep(1)
    return {
        "status": "success",
        "zoho_candidate_id": f"ZH-{str(uuid.uuid4())[:8].upper()}",
        "message": "Candidate successfully synced to Zoho ATS"
    }
