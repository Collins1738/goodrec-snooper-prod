"""
Slack webhook notifications — used in staging to surface poller activity.
"""
import httpx
from app.core.config import settings


def _send_slack(text: str) -> None:
    """Fire-and-forget POST to the configured Slack webhook."""
    if not settings.SLACK_WEBHOOK_URL:
        return
    try:
        response = httpx.post(
            settings.SLACK_WEBHOOK_URL,
            json={"text": text},
            timeout=5,
        )
        response.raise_for_status()
    except Exception as e:
        print(f"[slack] Failed to send notification: {e}")


def notify_poller_started() -> None:
    _send_slack("🟢 *Goodrec Snooper* — poller started, running every 15 minutes.")


def notify_event_found(event: dict, user_count: int) -> None:
    venue = event.get("venue_name", "Unknown venue")
    from app.services.goodrec import _format_start_time
    time_str = _format_start_time(event.get("start_time", ""))
    deeplink = event.get("deeplink", "")
    _send_slack(
        f"🏟️ *Free host slot detected!*\n"
        f"• Venue: {venue}\n"
        f"• Time: {time_str}\n"
        f"• Notifying {user_count} user(s)\n"
        f"• <{deeplink}|View on Goodrec>"
    )


def notify_poll_complete(events_checked: int, notified: int) -> None:
    _send_slack(
        f"🔄 *Poll complete* — checked {events_checked} unhosted event(s), sent {notified} notification(s)."
    )
