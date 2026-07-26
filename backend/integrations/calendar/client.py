import os
import uuid
import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from backend.config.settings import settings

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

async def schedule_calendar_interview(email: str, name: str, start_time_iso: str) -> dict:
    """
    Creates a Google Calendar event for an interview and generates a Jitsi Meet URL.
    Returns a dict containing the jitsi_url and event_id.
    """
    if not settings.GOOGLE_CALENDAR_ID:
        raise ValueError("GOOGLE_CALENDAR_ID is not configured in environment variables.")
        
    creds_json_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json_str:
        import json
        creds_info = json.loads(creds_json_str)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    else:
        credentials_path = settings.GOOGLE_CREDENTIALS_PATH
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Google credentials file not found at {credentials_path} and GOOGLE_CREDENTIALS_JSON not set.")
        creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
        
    service = build('calendar', 'v3', credentials=creds)
    
    # Generate Jitsi link
    meet_code = f"RecruiterAI-{uuid.uuid4().hex[:8]}"
    jitsi_url = f"https://meet.jit.si/{meet_code}"
    
    # Parse start time and set end time (+45 mins)
    # Expected format: "2023-10-25T10:00:00Z"
    try:
        start_dt = datetime.datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
    except ValueError:
        # Fallback to current time if parsing fails
        start_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
        
    end_dt = start_dt + datetime.timedelta(minutes=45)
    
    event = {
      'summary': f'Interview: {name} ({email})',
      'location': jitsi_url,
      'description': f'Technical interview scheduled. Candidate: {email}\n\nPlease join via the video link: {jitsi_url}',
      'start': {
        'dateTime': start_dt.isoformat(),
        'timeZone': 'UTC',
      },
      'end': {
        'dateTime': end_dt.isoformat(),
        'timeZone': 'UTC',
      },
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }

    event = service.events().insert(
        calendarId=settings.GOOGLE_CALENDAR_ID, 
        body=event
    ).execute()
    
    return {
        "event_id": event.get('id'),
        "jitsi_url": jitsi_url
    }
