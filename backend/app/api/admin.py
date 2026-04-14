# TODO: restrict to admin user (phone: +15713989671)

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import User, UserPreference, UserNotifiedEvent
from app.services.goodrec import fetch_unhosted_events, _save_tokens, _load_tokens

router = APIRouter(prefix="/admin", tags=["admin"])


class TokenSeedRequest(BaseModel):
    access_token: str
    refresh_token: str


@router.post("/tokens/seed")
async def seed_tokens(body: TokenSeedRequest):
    """Manually seed fresh Goodrec tokens into the DB (use when refresh token has expired)."""
    await _save_tokens(body.access_token, body.refresh_token)
    return {"ok": True, "message": "Tokens saved to DB."}


@router.get("/tokens/status")
async def token_status():
    """Check which tokens are currently active in the DB."""
    access_token, _ = await _load_tokens()
    # Decode expiry without exposing the raw token
    from app.services.goodrec import _jwt_expiry_epoch
    import time
    exp = _jwt_expiry_epoch(access_token)
    return {
        "access_token_preview": access_token[:20] + "...",
        "expires_at": exp,
        "expired": exp is not None and exp <= int(time.time()),
    }


@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    """Return all users with their subscribed venue keys."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()

    pref_result = await db.execute(select(UserPreference))
    prefs = pref_result.scalars().all()

    # Group venue_keys by user_id
    prefs_by_user: dict[str, list[str]] = {}
    for pref in prefs:
        prefs_by_user.setdefault(pref.user_id, []).append(pref.venue_key)

    return {
        "users": [
            {
                "id": u.id,
                "phone": u.phone,
                "verified": u.verified,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "venue_keys": prefs_by_user.get(u.id, []),
            }
            for u in users
        ],
        "total": len(users),
    }


@router.get("/games")
async def get_games(db: AsyncSession = Depends(get_db)):
    """Fetch live upcoming games from Goodrec and cross-reference subscribers."""
    events = await fetch_unhosted_events()

    # Load all preferences to map venue_key → list of user phones
    pref_result = await db.execute(
        select(UserPreference, User).join(User, UserPreference.user_id == User.id)
    )
    rows = pref_result.all()

    venue_to_phones: dict[str, list[str]] = {}
    for pref, user in rows:
        venue_to_phones.setdefault(pref.venue_key, []).append(user.phone)

    games = [
        {
            "event_id": ev["event_id"],
            "venue_key": ev["venue_key"],
            "venue_name": ev["venue_name"],
            "date": ev["date"],
            "start_time": ev["start_time"],
            "deeplink": ev["deeplink"],
            "subscribed_users": venue_to_phones.get(ev["venue_key"], []),
        }
        for ev in events
    ]

    return {"games": games}


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Return quick summary stats."""
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    verified_users = (
        await db.execute(select(func.count()).select_from(User).where(User.verified == True))
    ).scalar_one()
    total_subscriptions = (
        await db.execute(select(func.count()).select_from(UserPreference))
    ).scalar_one()
    total_notified_events = (
        await db.execute(select(func.count()).select_from(UserNotifiedEvent))
    ).scalar_one()

    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "total_subscriptions": total_subscriptions,
        "total_notified_events": total_notified_events,
    }
