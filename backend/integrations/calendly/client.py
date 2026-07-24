import httpx
from backend.config.settings import settings

async def schedule_calendly_interview(candidate_email: str, candidate_name: str):
    """
    Generates a single-use Calendly scheduling link for a candidate.
    """
    token = settings.CALENDLY_TOKEN
    event_uri = settings.CALENDLY_EVENT_TYPE_URI
    if not token or not event_uri:
        raise ValueError("CALENDLY_TOKEN or CALENDLY_EVENT_TYPE_URI not configured")
        
    api_url = "https://api.calendly.com/scheduling_links"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "max_event_count": 1,
        "owner": event_uri,
        "owner_type": "EventType"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("resource", {}).get("booking_url")
