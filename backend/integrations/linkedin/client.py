import httpx
from backend.config.settings import settings

async def import_linkedin_profile(linkedin_url: str):
    """
    Fetches LinkedIn profile data via Proxycurl API.
    """
    api_key = settings.PROXYCURL_API_KEY
    if not api_key:
        raise ValueError("PROXYCURL_API_KEY is not configured")
        
    headers = {'Authorization': f'Bearer {api_key}'}
    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
    params = {
        'linkedin_profile_url': linkedin_url,
        'fallback_to_cache': 'on-error',
        'use_cache': 'if-present',
        'skills': 'include',
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_endpoint, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
