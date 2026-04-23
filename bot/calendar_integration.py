import os
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
REMINDER_EMAIL = os.getenv("REMINDER_EMAIL")

def get_calendar_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def create_calendar_event(title: str, date: str, time: str) -> bool:
    try:
        service = get_calendar_service()

        start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(hours=1)

        event = {
            "summary": title,
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "attendees": [
                {"email": REMINDER_EMAIL}
            ],
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},
                    {"method": "popup", "minutes": 60},
                ],
            },
        }

        created = service.events().insert(
            calendarId="primary",
            body=event,
            sendUpdates="all"
        ).execute()

        print(f"Calendar event created: {created.get('htmlLink')}")
        return True

    except Exception as e:
        print(f"Calendar error: {e}")
        return False