"""
SMS webhook — receives inbound Twilio messages, routes to OpenClaw via
/v1/chat/completions (synchronous, session-aware), replies via Twilio SMS.

Pattern mirrors the Twitter DM daemon: stable session key per sender,
full conversation history maintained by OpenClaw.
"""
import httpx
from fastapi import APIRouter, Form, Response
from app.core.config import settings

router = APIRouter()

# All sensitive values come from env vars via settings


@router.post("/sms-webhook")
async def sms_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    To: str = Form(None),
    MessageSid: str = Form(None),
):
    """Receive inbound SMS, get Dravon's reply, send it back via Twilio."""
    print(f"[sms-webhook] Inbound SMS from {From}: {Body}")

    reply = await _ask_dravon(From, Body)

    if reply:
        await _send_sms(From, reply)

    # Empty TwiML — we handle the reply ourselves via Twilio API
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml",
    )


async def _ask_dravon(sender: str, message: str) -> str | None:
    """
    Call OpenClaw /v1/chat/completions synchronously with a stable session key.
    Same pattern as the Twitter DM daemon — maintains conversation history per sender.
    """
    session_key = f"sms-{sender}"
    is_collins = sender == settings.COLLINS_PHONE
    sender_label = "Collins (your human)" if is_collins else f"unknown sender {sender}"

    # Prefix the message with sender context so Dravon knows who's texting
    # Remind the agent to keep replies short — SMS has a 1600 char limit and truncation is bad UX
    prompt = (
        f"[SMS from {sender_label}]: {message}\n\n"
        f"(You are replying via SMS. Keep your response under 300 characters. "
        f"Be concise — no long explanations, no lists unless essential. "
        f"If a topic needs more detail, summarize and offer to elaborate.)"
    )

    body = {
        "model": "openclaw:main",
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{settings.OPENCLAW_GATEWAY_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENCLAW_GATEWAY_TOKEN}",
                    "Content-Type": "application/json",
                    "x-openclaw-agent-id": "main",
                    "x-openclaw-session-key": session_key,
                },
                json=body,
            )
            data = resp.json()
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"[sms-webhook] Dravon reply: {reply[:100]}")
            return reply or None
    except Exception as e:
        print(f"[sms-webhook] Failed to reach OpenClaw: {e}")
        return None


async def _send_sms(to: str, body: str) -> None:
    """Send SMS reply via Twilio."""
    # SMS character limit — truncate gracefully if needed
    if len(body) > 1600:
        body = body[:1597] + "..."

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json",
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                data={
                    "To": to,
                    "From": settings.TWILIO_FROM_NUMBER,
                    "Body": body,
                },
            )
            result = resp.json()
            if resp.status_code == 201:
                print(f"[sms-webhook] Reply sent: {result.get('sid')}")
            else:
                print(f"[sms-webhook] SMS send failed: {result.get('message')}")
    except Exception as e:
        print(f"[sms-webhook] Failed to send SMS reply: {e}")
