"""MCP server module"""

# -------IMPORTS---------
import datetime
import os.path
from loguru import logger

from mcp.server.fastmcp import FastMCP

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# -------INITIALIZATION---------
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

mcp = FastMCP("Google Calendar Agent")

CALENDAR_ID = "primary"  # Default calendar ID for the authenticated user


def init():
    """Connects to Google Calendar API"""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


# -------FUNCTIONALITIES---------


@mcp.tool()
def get_events():
    """Accesses the user's Google Calendar events"""
    logger.info("Accessing Google Calendar events...")
    try:
        # Call the Calendar API
        now = datetime.datetime.now(tz=datetime.UTC).isoformat()
        print("Getting the upcoming 10 events")
        events_result = (
            calendar.events()
            .list(
                calendarId=CALENDAR_ID,
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        response = events_result.get("items", [])

        if not response:
            response = "No upcoming events found."

        return response

    except HttpError as error:
        return {"error": str(error)}


if __name__ == "__main__":
    creds = init()
    calendar = build("calendar", "v3", credentials=creds)
    logger.info("Google Calendar Agent is running...")
    mcp.run()
