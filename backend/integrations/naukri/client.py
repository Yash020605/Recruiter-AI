import asyncio
from backend.config.settings import settings

async def import_candidate_profile(profile_url: str) -> dict:
    """Mock import of candidate profile from Naukri."""
    await asyncio.sleep(1)
    return {
        "status": "success",
        "naukri_id": f"NK-{abs(hash(profile_url)) % 10000}",
        "data": {
            "name": "Naukri Candidate",
            "email": "candidate@naukri.local",
            "phone": "9876543210",
            "current_company": "Tech Corp",
            "skills": "Python, React, AWS"
        }
    }
