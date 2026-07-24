import uuid
from backend.config.settings import settings

async def schedule_google_meet(email: str, name: str) -> str:
    """
    Generates a generic Google Meet URL. 
    In a real implementation, this would use google-api-python-client 
    and a Service Account JSON to create a calendar event with a conferenceData request.
    """
    # Generate a dummy meeting code format: abc-defg-hij
    code = f"{uuid.uuid4().hex[:3]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:3]}"
    return f"https://meet.google.com/{code}"
