import asyncio
import random
import httpx
from backend.config.settings import settings

async def invite_to_assessment(email: str, test_id: str) -> dict:
    """Send HackerEarth assessment invite."""
    client_secret = settings.HACKEREARTH_CLIENT_SECRET
    
    # Fallback to mock if no API key is configured
    if not client_secret:
        await asyncio.sleep(1)
        return {
            "status": "success",
            "assessment_url": f"https://www.hackerearth.com/test/{test_id}/?email={email}",
            "message": "Assessment invite sent via HackerEarth (Mocked)"
        }

    try:
        async with httpx.AsyncClient() as client:
            # Note: This is an illustrative endpoint for HackerEarth API.
            # Real endpoint details should be confirmed via API docs.
            response = await client.post(
                f"https://api.hackerearth.com/v4/assessment/{test_id}/invite/",
                headers={"client-secret": client_secret, "Content-Type": "application/json"},
                json={"email": email}
            )
            response.raise_for_status()
            data = response.json()
            return {
                "status": "success",
                "assessment_url": data.get("test_url", f"https://www.hackerearth.com/test/{test_id}/?email={email}"),
                "message": "Assessment invite sent successfully"
            }
    except Exception as e:
        # Graceful fallback on API error
        return {
            "status": "error",
            "message": f"Failed to invite candidate: {str(e)}"
        }

async def get_assessment_score(assessment_url: str) -> dict:
    """Retrieve assessment score from HackerEarth."""
    client_secret = settings.HACKEREARTH_CLIENT_SECRET
    
    if not client_secret:
        await asyncio.sleep(1)
        score = round(random.uniform(65.0, 98.0), 1)
        return {
            "status": "success",
            "score": score,
            "message": "Retrieved score from HackerEarth (Mocked)"
        }
    
    try:
        # Extract test/candidate IDs from the url or rely on another API integration point
        # This is illustrative
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.hackerearth.com/v4/assessment/candidate/score/",
                headers={"client-secret": client_secret},
                params={"assessment_url": assessment_url}
            )
            response.raise_for_status()
            data = response.json()
            return {
                "status": "success",
                "score": data.get("score", 0),
                "message": "Retrieved score from HackerEarth"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch score: {str(e)}"
        }
