"""
Goodrec API client — fetches unhosted events.
Ported from goodrec-snooper/snoop.py.
"""
from __future__ import annotations

import base64
import json
import time
from typing import Any

import httpx

from app.core.config import settings

# ── Constants ────────────────────────────────────────────────────────────────

NYC_CITY_ID = "334559f2-58b8-49d2-b2c4-5908a0688125"
SOCCER_CATEGORY_ID = "fa9a498d-732b-47b5-92bc-02bbe8676c6c"
DEVICE_ID = "9D93FB0C-1CD9-4F1F-B82D-A711D053E939"
PAGE_LIMIT = 15
API_BASE = "https://api.goodrec.tech"

# venue_key → exact title string as it appears in Goodrec events
VENUES: dict[str, dict] = {
    "socceroof_crown_heights": {
        "name": "Socceroof, Crown Heights",
        "title": "Socceroof, Crown Heights",
    },
    "socceroof_wall_street": {
        "name": "Socceroof, Wall Street",
        "title": "Socceroof Wall Street",
    },
}


# ── Public API ────────────────────────────────────────────────────────────────

async def fetch_unhosted_events(days: int = 7, max_pages: int = 50) -> list[dict]:
    """
    Fetch unhosted events across all tracked venues, covering `days` distinct dates.

    Handles token refresh transparently using settings.GOODREC_ACCESS_TOKEN /
    settings.GOODREC_REFRESH_TOKEN.

    Returns a list of dicts:
      { event_id, venue_key, venue_name, date, start_time, deeplink }
    """
    access_token = settings.GOODREC_ACCESS_TOKEN
    refresh_token = settings.GOODREC_REFRESH_TOKEN

    # Refresh if needed
    if _token_is_expiring_soon(access_token):
        access_token, refresh_token = await _refresh_tokens(access_token, refresh_token)
        # TODO: persist updated tokens back to settings/DB if needed

    # Build title → venue_key lookup
    title_to_key = {info["title"]: key for key, info in VENUES.items()}

    seen_dates: list[str] = []
    all_rows: list[dict] = []

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        for page in range(1, max_pages + 1):
            rows = await _fetch_events_page(client, access_token, page)

            for row in rows:
                date = row.get("date")
                if date and date not in seen_dates:
                    seen_dates.append(date)

            all_rows.extend(rows)

            if len(seen_dates) >= days:
                break

    # Filter to unhosted events in tracked venues
    unhosted: list[dict] = []
    for row in all_rows:
        if row.get("hostName") is not None:
            continue
        venue_key = title_to_key.get(row.get("title", ""))
        if not venue_key:
            continue
        unhosted.append({
            "event_id": row["id"],
            "venue_key": venue_key,
            "venue_name": VENUES[venue_key]["name"],
            "date": row.get("date", ""),
            "start_time": row.get("startTime", ""),
            "deeplink": row.get("deeplink", f"https://goodrec.com/games/{row['id']}"),
        })

    return unhosted

# ── Core fetch ────────────────────────────────────────────────────────────────

async def _fetch_events_page(client: httpx.AsyncClient, access_token: str, page: int) -> list[dict]:
    """Fetch one page of events. Returns flattened event rows with `date` attached."""
    url = (
        f"{API_BASE}/api/v2/events"
        f"?page={page}&limit={PAGE_LIMIT}"
        f"&cityId={NYC_CITY_ID}&categoryId={SOCCER_CATEGORY_ID}"
    )
    resp = await client.get(url, headers=_build_headers(access_token), timeout=30.0)
    resp.raise_for_status()
    return _parse_and_flatten(resp.json())


def _parse_and_flatten(payload: Any) -> list[dict]:
    """Parse Goodrec events response and flatten to a list of event rows."""
    groups = payload
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        groups = payload["data"]

    if not isinstance(groups, list):
        return []

    rows: list[dict] = []
    for g in groups:
        if not isinstance(g, dict):
            continue
        date = g.get("date")
        events = g.get("events")
        if not isinstance(events, list):
            continue
        for ev in events:
            if not isinstance(ev, dict):
                continue
            rows.append({
                "date": date,
                "id": ev.get("id"),
                "title": ev.get("title"),
                "hostName": ev.get("hostName"),
                "startTime": ev.get("startTime"),
                "price": ev.get("price"),
                "hasPromoPrice": ev.get("hasPromoPrice"),
                "promoPrice": ev.get("promoPrice"),
                "deeplink": ev.get("deeplink"),
                "bookingCountDisplay": ev.get("bookingCountDisplay"),
                "createdAt": ev.get("createdAt"),
            })
    return rows

# ── Token helpers ─────────────────────────────────────────────────────────────

def _jwt_expiry_epoch(token: str) -> int | None:
    """Extract `exp` claim from JWT without verifying signature."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
        exp = payload.get("exp")
        return int(exp) if exp is not None else None
    except Exception:
        return None


def _token_is_expiring_soon(token: str, skew_seconds: int = 120) -> bool:
    exp = _jwt_expiry_epoch(token)
    if exp is None:
        return False
    return exp <= int(time.time()) + skew_seconds


def _build_headers(access_token: str) -> dict[str, str]:
    return {
        "Host": "api.goodrec.tech",
        "Authorization": f"Bearer {access_token}",
        "Accept-Charset": "UTF-8",
        "Accept-Language": "en-US,en;q=0.9",
        "X-App-Version-Code": "29",
        "Accept": "application/json",
        "User-Agent": "ktor-client",
        "Connection": "keep-alive",
        "X-Device-ID": DEVICE_ID,
        "X-App-Version": "2.0.0",
        "X-Platform": "iOS",
    }


async def _refresh_tokens(access_token: str, refresh_token: str) -> tuple[str, str]:
    """Call /api/v2/auth/refresh and return (new_access_token, new_refresh_token)."""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.post(
            f"{API_BASE}/api/v2/auth/refresh",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
                "X-Device-ID": DEVICE_ID,
            },
            json={"refreshToken": refresh_token},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["accessToken"], data["refreshToken"]

# ── Formatting helpers ────────────────────────────────────────────────────────

def _format_start_time(start_time: str) -> str:
    """Convert ISO startTime to a friendly string like 'Fri 28th March, 7PM'."""
    import datetime
    try:
        dt = datetime.datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        n = dt.day
        if 11 <= n <= 13:
            ordinal = f"{n}th"
        else:
            ordinal = f"{n}{['th','st','nd','rd','th'][min(n % 10, 4)]}"
        return f"{dt.strftime('%a')} {ordinal} {dt.strftime('%B')}, {dt.strftime('%-I%p')}"
    except Exception:
        return start_time


