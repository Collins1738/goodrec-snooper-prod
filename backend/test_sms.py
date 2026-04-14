"""
Quick SMS test script — uses real prod Twilio creds directly (bypasses is_test_env gate).
Run with: python3 test_sms.py
Requires: venv activated (source venv/bin/activate)
"""
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

msg = client.messages.create(
    to="+15713989671",
    from_=os.environ["TWILIO_FROM_NUMBER"],
    body="hey brudda, this is a test from goodrec-snooper 🔔 — if you got this, Twilio is live!",
)

print("Status:", msg.status)
print("SID:", msg.sid)
