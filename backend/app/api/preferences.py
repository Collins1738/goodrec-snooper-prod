from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.database import get_db
from app.db.models import UserPreference
from app.core.security import get_current_user
from app.services.goodrec import VENUES

router = APIRouter(prefix="/preferences", tags=["preferences"])


class PreferencesUpdate(BaseModel):
    venue_keys: list[str]


@router.get("")
async def get_preferences(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    prefs = result.scalars().all()
    return {"venue_keys": [p.venue_key for p in prefs]}


@router.put("")
async def update_preferences(
    body: PreferencesUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate venue keys
    invalid = [k for k in body.venue_keys if k not in VENUES]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Unknown venue keys: {invalid}")

    # Replace all preferences for this user
    await db.execute(delete(UserPreference).where(UserPreference.user_id == user_id))
    for key in body.venue_keys:
        db.add(UserPreference(user_id=user_id, venue_key=key))

    await db.commit()
    return {"venue_keys": body.venue_keys}
