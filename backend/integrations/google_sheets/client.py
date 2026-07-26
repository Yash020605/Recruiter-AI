import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from backend.config.settings import settings

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

async def export_to_google_sheets(candidate_data: dict) -> dict:
    """
    Exports candidate data to a Google Sheet using the Google Sheets API v4.
    """
    if not settings.GOOGLE_SHEET_ID:
        raise ValueError("GOOGLE_SHEET_ID is not configured in environment variables.")
        
    # Load credentials
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
        
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # Prepare values (Name, Email, Phone, Status, Match Score)
    values = [
        [
            candidate_data.get("name", ""),
            candidate_data.get("email", ""),
            candidate_data.get("phone", ""),
            candidate_data.get("status", ""),
            candidate_data.get("score", "")
        ]
    ]
    body = {'values': values}
    
    # Append to Sheet1
    range_name = 'Sheet1!A:E'
    
    result = sheet.values().append(
        spreadsheetId=settings.GOOGLE_SHEET_ID,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    
    updated_cells = result.get('updates', {}).get('updatedCells', 0)
    
    return {
        "status": "success", 
        "message": f"Data appended to Google Sheets ({updated_cells} cells updated)."
    }
