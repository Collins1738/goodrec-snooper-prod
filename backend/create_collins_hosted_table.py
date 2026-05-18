"""
One-off migration: create the collins_hosted_events table.
Run once on the Railway prod database.
"""
import asyncio
from app.db.database import engine
from sqlalchemy import text


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS collins_hosted_events (
    event_id          VARCHAR PRIMARY KEY,
    calendar_event_id VARCHAR NOT NULL,
    venue_name        VARCHAR NOT NULL,
    start_time        VARCHAR NOT NULL,
    calendared_at     TIMESTAMP DEFAULT NOW()
);
"""


async def main():
    async with engine.begin() as conn:
        await conn.execute(text(CREATE_TABLE_SQL))
    print("Done — collins_hosted_events table created (or already existed).")


asyncio.run(main())
