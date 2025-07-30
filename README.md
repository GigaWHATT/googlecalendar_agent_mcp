# Google Calendar Agent (MCP Application)

---

## Overview

This is a Model Context Protocol (MCP) agent that integrates with the Google Calendar API. It allows users to:

- Retrieve upcoming events
- Create new calendar events
- Delete existing events
- Delay events by a given time

---

## Requirements

- Python 3.8+
- Google API credentials (`credentials.json`)
- Installed packages:
  - `loguru`
  - `google-auth`
  - `google-auth-oauthlib`
  - `google-api-python-client`
  - `mcp` (FastMCP)

---

## Setup

1. **Google API Credentials:**

   - Create a project and enable the Google Calendar API in the Google Cloud Console.
   - Download `credentials.json` for OAuth 2.0 client ID.
   - Place `credentials.json` in the same directory as this script.

2. **Install Python packages:**

   ```bash
   pip install loguru google-auth google-auth-oauthlib google-api-python-client mcp
