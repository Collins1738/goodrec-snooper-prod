from fastapi import APIRouter
from app.services.goodrec import VENUES

router = APIRouter(prefix="/venues", tags=["venues"])


@router.get("")
async def list_venues():
    return [
        {"key": key, "name": info["name"]}
        for key, info in VENUES.items()
    ]
