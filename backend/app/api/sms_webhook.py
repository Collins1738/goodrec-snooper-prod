"""
SMS webhook — receives inbound Twilio messages, fires to OpenClaw gateway async,
returns empty TwiML immediately. Dravon processes and replies via SMS independently.
"""
import httpx
from fastapi import APIRouter, Form, Response
from app.core.config import settings

router = APIRouter()

OPENCLAW_GATEWAY_URL = "https://dravon-macbook.tail2c66c1.ts.net"
OPENCLAW_HOOKS_TOKEN = "22249720bf94a52321bac5f96c9eca87c2cecb27c37651fd"


@router.post("/sms-webhook")
async def sms_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    To: str = Form(None),
    MessageSid: str = Form(None),
):
    """Receive inbound SMS, kick off Dravon async, return empty TwiML."""
    print(f"[sms-webhook] Inbound SMS from {From}: {Body}")

    # Fire and forget — don't wait for Dravon's response
    await _wake_dravon(From, Body)

    # Empty TwiML — Twilio won't send any auto-reply, Dravon handles it
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml",
    )


async def _wake_dravon(sender: str, message: str) -> None:
    """POST to OpenClaw /hooks/agent — async, fire and forget."""
    payload = {
        "message": (
            f"Inbound SMS from {sender}: {message}\n\n"
            f"Reply to this SMS. Use the send_sms.js script or Twilio API directly "
            f"(account SID: {settings.TWILIO_ACCOUNT_SID}, "
            f"auth token: {settings.TWILIO_AUTH_TOKEN}, "
            f"from: {settings.TWILIO_FROM_NUMBER}) to send your reply to {sender}. "
            f"Keep the reply concise — it's going via SMS."
        ),
        "name": "SMS",
        "wakeMode": "now",
        "deliver": False,
        "sessionKey": f"hook:sms:{sender}",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{OPENCLAW_GATEWAY_URL}/hooks/agent",
                headers={
                    "Authorization": f"Bearer {OPENCLAW_HOOKS_TOKEN}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            print(f"[sms-webhook] Gateway responded {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"[sms-webhook] Failed to reach OpenClaw gateway: {e}")
