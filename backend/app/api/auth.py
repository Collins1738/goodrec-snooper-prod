from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.db.models import User
from app.services.twilio import send_otp, verify_otp
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class PhoneRequest(BaseModel):
    phone: str  # E.164 format: +12125551234


class VerifyRequest(BaseModel):
    phone: str
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def normalize_phone(phone: str) -> str:
    """Ensure phone is in E.164 format. Assumes US number if no country code."""
    digits = "".join(c for c in phone if c.isdigit())
    if phone.startswith("+"):
        return "+" + digits
    if len(digits) == 10:
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    return "+" + digits


@router.post("/send-otp")
async def send_otp_endpoint(body: PhoneRequest, db: AsyncSession = Depends(get_db)):
    phone = normalize_phone(body.phone)
    # Create user if doesn't exist
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        user = User(phone=phone)
        db.add(user)
        await db.commit()

    send_otp(phone)
    return {"message": "OTP sent"}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp_endpoint(body: VerifyRequest, db: AsyncSession = Depends(get_db)):
    phone = normalize_phone(body.phone)
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    approved = verify_otp(phone, body.code)
    if not approved:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    user.verified = True
    await db.commit()

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)
