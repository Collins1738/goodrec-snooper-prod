"""
Google Calendar integration — creates event blocks for Collins's hosted Goodrec games.
Uses OAuth2 refresh token to get short-lived access tokens and hits the Calendar REST API directly.
"""
from __future__ import annotations

import httpx
from datetime import datetime, timedelta, timezone

from app.core.config import settings

CALENDAR_ID = "hey.dravon@gmail.com"
COLLINS_EMAIL = "tobechikeluba@gmail.com"

TOKEN_URL = "https://oauth2.googleapis.com/token"
CALENDAR_API_BASE = "https://www.googleapis.com/calendar/v3"

EVENT_DURATION_MINUTES = 90
REMINDER_MINUTES_BEFORE = 30


async def _get_access_token() -> str:
    """Exchange the stored refresh token for a short-lived access token."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(TOKEN_URL, data={
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": settings.GOOGLE_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        })
        resp.raise_for_status()
        return resp.json()["access_token"]


async def create_event(event: dict) -> str:
    """
    Create a Google Calendar event for a hosted Goodrec game.

    `event` should have: venue_name, start_time (ISO string), deeplink

    Returns the created calendar event ID.
    """
    access_token = await _get_access_token()

    import zoneinfo
    eastern = zoneinfo.ZoneInfo("America/New_York")
    start_dt = datetime.fromisoformat(event["start_time"].replace("Z", "+00:00")).astimezone(eastern)
    end_dt = start_dt + timedelta(minutes=EVENT_DURATION_MINUTES)

    body = {
        "summary": f"⚽ Goodrec @ {event['venue_name']}",
        "description": f"Your hosted Goodrec game.\n\n{event.get('deeplink', '')}",
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "America/New_York",
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "America/New_York",
        },
        "attendees": [
            {"email": COLLINS_EMAIL, "role": "writer"},
        ],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": REMINDER_MINUTES_BEFORE},
            ],
        },
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{CALENDAR_API_BASE}/calendars/{CALENDAR_ID}/events",
            headers={"Authorization": f"Bearer {access_token}"},
            json=body,
        )
        resp.raise_for_status()
        return resp.json()["id"]



async def delete_event(calendar_event_id: str) -> None:
    """Delete a Google Calendar event by its ID."""
    access_token = await _get_access_token()
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.delete(
            f"{CALENDAR_API_BASE}/calendars/{CALENDAR_ID}/events/{calendar_event_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        # 404 = already deleted, that's fine
        if resp.status_code not in (200, 204, 404):
            resp.raise_for_status()
