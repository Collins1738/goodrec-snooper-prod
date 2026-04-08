from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.api import auth, venues, preferences, admin
from app.jobs.poller import poll_and_notify

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the 15-min polling job
    scheduler.add_job(poll_and_notify, "interval", minutes=15, id="poller")
    scheduler.start()
    print("[scheduler] Poller started — running every 15 minutes")
    yield
    scheduler.shutdown()


app = FastAPI(title="Goodrec Snooper", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(venues.router)
app.include_router(preferences.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
