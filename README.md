# goodrec-snooper-prod

SMS alerts for free host slots on Goodrec.

## Stack
- **Backend:** FastAPI (Python 3.11+) + PostgreSQL + Twilio — deployed on **Railway**
- **Frontend:** React + Vite + Tailwind CSS — deployed on **Vercel**
- **Scheduler:** APScheduler (15-min polling)

## Deployments
- **Backend (Railway):** https://goodrec-snooper-prod-production.up.railway.app
- **Frontend (Vercel):** *(add Vercel URL here)*

---

## Database (Docker)

```bash
# Start Postgres
docker run -d \
  --name goodrec-snooper-db \
  -e POSTGRES_USER=goodrec \
  -e POSTGRES_PASSWORD=goodrec \
  -e POSTGRES_DB=goodrec_snooper \
  -p 5432:5432 \
  postgres:16

# Stop / start later
docker stop goodrec-snooper-db
docker start goodrec-snooper-db

# Useful commands
docker ps                          # view running containers
docker ps -a                       # view all containers (including stopped)
docker images                      # list downloaded images
docker logs goodrec-snooper-db     # view Postgres logs
docker exec -it goodrec-snooper-db psql -U goodrec goodrec_snooper  # open psql shell
```

Update `backend/.env`:
```
DATABASE_URL=postgresql+asyncpg://goodrec:goodrec@localhost:5432/goodrec_snooper
```

---

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# cp .env.example .env
# Fill in .env with your DB URL, JWT secret, Twilio creds

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### DB Migrations (Alembic)

```bash
alembic init alembic
# Configure alembic.ini + env.py to use DATABASE_URL
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

The Vite dev server proxies `/api/*` → `http://localhost:8000`.

---

## TODO
- [ ] Wire up real Goodrec API params in `services/goodrec.py`
- [ ] Add `TWILIO_FROM_NUMBER` to config + .env.example
- [ ] Set up Alembic migrations
- [ ] Add unsubscribe flow (reply STOP or settings page)
- [ ] Tighten CORS in production
- [ ] Deploy to DigitalOcean
