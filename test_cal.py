import asyncio
from backend.integrations.calendar.client import settings, build, Credentials, SCOPES, uuid, datetime

async def schedule_calendar_interview_test(email: str, name: str, start_time_iso: str) -> dict:
    credentials_path = settings.GOOGLE_CREDENTIALS_PATH
    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    
    meet_code = f"RecruiterAI-{uuid.uuid4().hex[:8]}"
    jitsi_url = f"https://meet.jit.si/{meet_code}"
    
    start_dt = datetime.datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
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
    }

    event = service.events().insert(
        calendarId=settings.GOOGLE_CALENDAR_ID, 
        body=event
    ).execute()
    
    return {
        "event_id": event.get('id'),
        "jitsi_url": jitsi_url
    }

async def main():
    try:
        res = await schedule_calendar_interview_test("test@example.com", "Test User", "2023-11-01T10:00:00Z")
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
