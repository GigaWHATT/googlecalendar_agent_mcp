# Google Calendar Agent (MCP)

---

## Overview

This is a Model Context Protocol (MCP) agent that integrates with the Google Calendar API. It allows users to:

- Retrieve upcoming events
- Create new calendar events
- Delete existing events
- Delay events by a given time

---

## Requirements

To install requirements, use the following command:
```bash
pip install -r requirements.txt
```

---

## Setup

**Google API Credentials:**

To set up authentication, you'll need to follow the instructions on <url>https://developers.google.com/workspace/calendar/api/quickstart/python?hl=en<url>.

When you've created your client (as a Desktop Application) a pop-up will appear summarising your client's details. Click 'Download to JSON' and download the file as ```credentials.json``` into the root repository of this project.

When you run the program for the first time (see 'Run the code' section), a window will appear asking you to login to your Google account. This happens only on the first run. Please follow the instructions on the pop-up.

**Model accesses**

To have access to a model, you'll need to create an environment variable file:
```bash
touch .env
```
Then, you'll need to enter your API token as an environment variable:
```bash
echo AZURE_OPENAI_API_KEY=<your_key_here> >> .env
```

---

## Run the code
```bash
python src/main.py
```
Use this command to run the code. After that, you're all set to interact with the agent in the Terminal.



## Tools

Here is a description of the provided tools.

## get_events()

Retrieves up to 10 upcoming events from the user's primary Google Calendar.

**Returns:**
- A list of upcoming events, or
- A message if no events are found, or
- An error dictionary if an API error occurs.


## create_event(start_time, title, start_date=None, end_date=None, end_time=None)

Creates a new event in the user's Google Calendar.

**Parameters:**
- `start_time` (datetime.time): Event start time (required).
- `title` (str): Event title (required).
- `start_date` (datetime.date, optional): Start date, defaults to today.
- `end_date` (datetime.date, optional): End date, defaults to start_date if not provided.
- `end_time` (datetime.time, optional): End time, defaults to start_time + 1 hour if not provided.

**Returns:**
- Success message if created, or
- An error dictionary if an API error occurs.



## delete_event(name, date=None)

Deletes events matching the given name and optionally date.

**Parameters:**
- `name` (str): Name of the event to delete (required).
- `date` (datetime.date, optional): Date of the event to delete. If omitted, deletes all matching events by name.

**Returns:**
- Success message if deleted, or
- Message if no matching event found, or
- An error dictionary if an API error occurs.



## delay_event(time, name)

Delays all events matching the given name by a specified time delta.

**Parameters:**
- `time` (datetime.timedelta): Amount of time to delay the event(s) by (required).
- `name` (str): Name of the event(s) to delay (required).

**Returns:**
- Success message with delay duration, or
- An error dictionary if an API error occurs.

---

## Annex

In case of any issues, you can create an issue report on the github.
