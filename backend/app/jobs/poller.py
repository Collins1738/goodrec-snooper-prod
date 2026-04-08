"""
15-minute polling job — checks Goodrec for unhosted events and sends SMS alerts.
In staging, also fires Slack webhook notifications for observability.
"""
from sqlalchemy import select
from app.core.config import settings
from app.db.database import AsyncSessionLocal
from app.db.models import User, UserPreference, UserNotifiedEvent
from app.services.goodrec import fetch_unhosted_events
from app.services.twilio import send_sms
from app.services import slack


async def poll_and_notify():
    print("[poller] Running poll...")
    try:
        unhosted_events = await fetch_unhosted_events()
        if not unhosted_events:
            print("[poller] No unhosted events found.")
            if settings.is_test_env:
                slack.notify_poll_complete(0, 0)
            return

        total_notified = 0
        async with AsyncSessionLocal() as db:
            for event in unhosted_events:
                count = await _notify_users_for_event(db, event)
                total_notified += count

        print(f"[poller] Done. Checked {len(unhosted_events)} unhosted events, notified {total_notified}.")
        if settings.is_test_env:
            slack.notify_poll_complete(len(unhosted_events), total_notified)

    except Exception as e:
        print(f"[poller] Error: {e}")
        if settings.is_test_env:
            slack.notify_poll_complete(-1, 0)


async def _notify_users_for_event(db, event: dict) -> int:
    """Notify eligible users for a single event. Returns number of users notified."""
    event_id = event["event_id"]
    venue_key = event["venue_key"]

    # Find users subscribed to this venue who haven't been notified yet
    result = await db.execute(
        select(User)
        .join(UserPreference, UserPreference.user_id == User.id)
        .where(
            UserPreference.venue_key == venue_key,
            User.verified == True,
            ~User.id.in_(
                select(UserNotifiedEvent.user_id).where(
                    UserNotifiedEvent.event_id == event_id
                )
            ),
        )
    )
    users = result.scalars().all()

    if not users:
        return 0

    from app.services.goodrec import _format_start_time
    time_str = _format_start_time(event.get("start_time", ""))
    msg = (
        f"🏟️ Free host slot open! {event['venue_name']} — {time_str}. "
        f"Claim it: {event['deeplink']}"
    )

    notified = 0
    for user in users:
        try:
            send_sms(user.phone, msg)
            db.add(UserNotifiedEvent(user_id=user.id, event_id=event_id))
            print(f"[poller] Notified {user.phone} for event {event_id}")
            notified += 1
        except Exception as e:
            print(f"[poller] Failed to notify {user.phone}: {e}")

    await db.commit()
    return notified
