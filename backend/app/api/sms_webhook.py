"""
SMS webhook — receives inbound Twilio messages and forwards them to Slack.
Twilio posts form-encoded data to this endpoint when a text is received.
"""
import httpx
from fastapi import APIRouter, Form, Response
from app.core.config import settings

router = APIRouter()


@router.post("/sms-webhook")
async def sms_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    To: str = Form(None),
    MessageSid: str = Form(None),
):
    """Receive inbound SMS from Twilio and forward to Slack."""
    print(f"[sms-webhook] Inbound SMS from {From}: {Body}")

    await _forward_to_slack(From, Body)

    # Return empty TwiML response — tells Twilio we handled it (no auto-reply)
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml",
    )


async def _forward_to_slack(sender: str, message: str) -> None:
    """Post inbound SMS to Dravon's Slack channel via bot token."""
    bot_token = settings.SLACK_BOT_TOKEN
    channel = settings.DRAVON_SLACK_CHANNEL

    if not bot_token or not channel:
        print("[sms-webhook] Missing SLACK_BOT_TOKEN or DRAVON_SLACK_CHANNEL — skipping Slack forward")
        return

    text = f"📱 *SMS from {sender}:*\n{message}"

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {bot_token}"},
                json={"channel": channel, "text": text},
            )
            data = resp.json()
            if not data.get("ok"):
                print(f"[sms-webhook] Slack post failed: {data.get('error')}")
    except Exception as e:
        print(f"[sms-webhook] Failed to forward to Slack: {e}")
