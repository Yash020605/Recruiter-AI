import asyncio
import random
from backend.config.settings import settings

async def invite_to_assessment(email: str, test_id: str) -> dict:
    """Mock sending HackerEarth assessment invite."""
    await asyncio.sleep(1)
    return {
        "status": "success",
        "assessment_url": f"https://www.hackerearth.com/test/{test_id}/?email={email}",
        "message": "Assessment invite sent via HackerEarth"
    }

async def get_assessment_score(assessment_url: str) -> dict:
    """Mock retrieving assessment score from HackerEarth."""
    await asyncio.sleep(1)
    score = round(random.uniform(65.0, 98.0), 1)
    return {
        "status": "success",
        "score": score,
        "message": "Retrieved score from HackerEarth"
    }
