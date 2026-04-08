"""Quick script to create all DB tables from models. Run once to initialize."""
import asyncio
from app.db.database import engine, Base
import app.db.models  # noqa: F401 — registers models on Base


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")

asyncio.run(main())
