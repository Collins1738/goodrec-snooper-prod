from twilio.rest import Client
from app.core.config import settings

_client = Client(settings.twilio_sid, settings.twilio_token)


def send_otp(phone: str) -> None:
    _client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID) \
        .verifications.create(to=phone, channel="sms")


def verify_otp(phone: str, code: str) -> bool:
    result = _client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID) \
        .verification_checks.create(to=phone, code=code)
    return result.status == "approved"


def send_sms(phone: str, message: str) -> None:
    # Uses Verify messaging service — swap to Twilio Messaging if needed
    _client.messages.create(
        to=phone,
        from_=settings.TWILIO_FROM_NUMBER,
        body=message,
    )


# See .env for Twilio credentials (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, etc.)