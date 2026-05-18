"""
15-minute polling job — checks Goodrec for unhosted events and sends SMS alerts.
Also checks for events hosted by Collins and adds them to his Google Calendar.
In staging, also fires Slack webhook notifications for observability.
"""
from sqlalchemy import select
from app.core.config import settings
from app.db.database import AsyncSessionLocal
from app.db.models import User, UserPreference, UserNotifiedEvent, CollinsHostedEvent
from app.services.goodrec import fetch_unhosted_events, fetch_my_hosted_events
from app.services.twilio import send_sms
from app.services import slack, calendar


async def poll_and_notify():
    print("[poller] Running poll...")
    try:
        unhosted_events = await fetch_unhosted_events()
        if not unhosted_events:
            print("[poller] No unhosted events found.")
        else:
            total_notified = 0
            async with AsyncSessionLocal() as db:
                for event in unhosted_events:
                    count = await _notify_users_for_event(db, event)
                    total_notified += count
            print(f"[poller] Checked {len(unhosted_events)} unhosted events, notified {total_notified}.")

        await _calendar_sync_hosted_events()

    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {e}" if str(e) else repr(e)
        tb = traceback.format_exc()
        print(f"[poller] Error: {error_detail}\n{tb}")
        from app.services.slack import notify_poller_error
        notify_poller_error(f"{error_detail}\n```{tb[-1000:]}```")


async def _calendar_sync_hosted_events():
    """Check for Collins's hosted events and add any new ones to Google Calendar."""
    try:
        my_events = await fetch_my_hosted_events()
        if not my_events:
            print("[poller] No hosted events found for Collins.")
            return

        print(f"[poller] Found {len(my_events)} hosted event(s) for Collins.")
        async with AsyncSessionLocal() as db:
            for event in my_events:
                await _maybe_calendar_event(db, event)

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[poller] Calendar sync error: {e}\n{tb}")


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


async def _maybe_calendar_event(db, event: dict) -> None:
    """Add a Google Calendar event for a hosted game if we haven't already."""
    event_id = event["event_id"]

    # Check if already calendared
    result = await db.execute(
        select(CollinsHostedEvent).where(CollinsHostedEvent.event_id == event_id)
    )
    if result.scalar_one_or_none():
        return  # Already handled

    try:
        cal_event_id = await calendar.create_event(event)
        db.add(CollinsHostedEvent(
            event_id=event_id,
            calendar_event_id=cal_event_id,
            venue_name=event["venue_name"],
            start_time=event["start_time"],
        ))
        await db.commit()
        print(f"[poller] Added calendar event for hosted game {event_id} @ {event['venue_name']}")
    except Exception as e:
        print(f"[poller] Failed to create calendar event for {event_id}: {e}")
