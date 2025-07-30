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


@mcp.tool()
def create_event(
    start_date: datetime.date,
    start_time: datetime.time,
    title: str,
    end_date: datetime.date | None = None,
    end_time: datetime.time | None = None,
    date_type: str | None = "event",
) -> str:
    """Creates an event in the user's Google calendar.

    Args:
        start_date (datetime.date): date of start of event
        start_time (datetime.time): time of start of event
        title (str): title of event
        end_date (Optional[datetime.date], optional): end date of event. Defaults to None.
        end_time (Optional[datetime.time], optional): end time of event. Defaults to None.
        date_type (Optional[str], optional): can be either event, task or appointment. Defaults to 'event'.

    Returns:
        _type_: result or error message
    """
    logger.info("Creating a new event in Google Calendar...")
    try:
        if not end_date:
            end_date = start_date

        if not end_time:
            end_time = (
                datetime.datetime.combine(start_date, start_time)
                + datetime.timedelta(hours=1)
            ).time()

        start_datetime = datetime.datetime.combine(start_date, start_time)
        end_datetime = datetime.datetime.combine(end_date, end_time)

        event = {
            "summary": title,
            "start": {"dateTime": start_datetime.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_datetime.isoformat(), "timeZone": "UTC"},
        }
        logger.info(f"Creating event: {event}")

        if date_type == "event":
            calendar.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        elif date_type == "task":
            calendar.tasks().insert(calendarId=CALENDAR_ID, body=event).execute()
        elif date_type == "appointment":
            calendar.appointments().insert(calendarId=CALENDAR_ID, body=event).execute()

        return f"Event '{title}' created successfully."

    except HttpError as error:
        logger.info(f"HTTP error in create_event: {error}")
        return {"error": str(error)}


if __name__ == "__main__":
    creds = init()
    calendar = build("calendar", "v3", credentials=creds)
    logger.info("Google Calendar Agent is running...")
    mcp.run()
    # create_event(datetime.date(2025, 7, 3), datetime.time(10, 0), "Test Event")
