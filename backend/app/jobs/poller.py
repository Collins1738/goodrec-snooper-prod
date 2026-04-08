"""
15-minute polling job — checks Goodrec for unhosted events and sends SMS alerts.
"""
from sqlalchemy import select, text
from app.db.database import AsyncSessionLocal
from app.db.models import User, UserPreference, UserNotifiedEvent
from app.services.goodrec import fetch_unhosted_events
from app.services.twilio import send_sms


async def poll_and_notify():
    print("[poller] Running poll...")
    try:
        unhosted_events = await fetch_unhosted_events()
        if not unhosted_events:
            print("[poller] No unhosted events found.")
            return

        async with AsyncSessionLocal() as db:
            for event in unhosted_events:
                await _notify_users_for_event(db, event)

        print(f"[poller] Done. Checked {len(unhosted_events)} unhosted events.")
    except Exception as e:
        print(f"[poller] Error: {e}")


async def _notify_users_for_event(db, event: dict):
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

    for user in users:
        from app.services.goodrec import _format_start_time
        time_str = _format_start_time(event.get("start_time", ""))
        msg = (
            f"🏟️ Free host slot open! {event['venue_name']} — {time_str}. "
            f"Claim it: {event['deeplink']}"
        )
        try:
            send_sms(user.phone, msg)
            db.add(UserNotifiedEvent(user_id=user.id, event_id=event_id))
            print(f"[poller] Notified {user.phone} for event {event_id}")
        except Exception as e:
            print(f"[poller] Failed to notify {user.phone}: {e}")

    await db.commit()
