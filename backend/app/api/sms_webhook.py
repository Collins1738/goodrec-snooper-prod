"""
SMS webhook — receives inbound Twilio messages, generates a reply via Claude,
and sends it back to the sender via Twilio SMS (TwiML response).
"""
import httpx
from fastapi import APIRouter, Form, Response
from app.core.config import settings

router = APIRouter()

DRAVON_SYSTEM_PROMPT = """You are Dravon, a personal AI assistant for Collins. 
You're responding to an SMS message Collins sent you. Be concise, helpful, and friendly — this is a text message so keep replies short.
Signature phrases (use naturally): "alright boss", "yes boss", "tough times 😬", "brudda".
Collins's full name is Collins Chikeluba. He lives in Brooklyn, NY. He's a software engineer."""


@router.post("/sms-webhook")
async def sms_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    To: str = Form(None),
    MessageSid: str = Form(None),
):
    """Receive inbound SMS from Collins, reply via Claude."""
    print(f"[sms-webhook] Inbound SMS from {From}: {Body}")

    reply = await _generate_reply(Body)

    # Reply via TwiML — Twilio sends this back as an SMS automatically
    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{_escape_xml(reply)}</Message></Response>'
    return Response(content=twiml, media_type="application/xml")


async def _generate_reply(message: str) -> str:
    """Call Anthropic API to generate a reply."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-haiku-4-5",
                    "max_tokens": 300,
                    "system": DRAVON_SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": message}],
                },
            )
            data = resp.json()
            return data["content"][0]["text"]
    except Exception as e:
        print(f"[sms-webhook] Claude call failed: {e}")
        return "hey something went wrong on my end, try again in a sec 😬"


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )
