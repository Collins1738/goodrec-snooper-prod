# goodrec-snooper-prod

SMS alerts for free host slots on Goodrec.

## Stack
- **Backend:** FastAPI (Python 3.11+) + PostgreSQL + Twilio — deployed on **Railway**
- **Frontend:** React + Vite + Tailwind CSS — deployed on **Vercel**
- **Scheduler:** APScheduler (15-min polling)

## Deployments

### Production
- **Backend (Railway):** https://goodrec-snooper-prod-production.up.railway.app
- **Frontend (Vercel):** https://snoop.sallova.com
- **Branch:** `main`

### Staging
- **Backend (Railway):** https://goodrec-snooper-prod-staging.up.railway.app
- **Frontend (Vercel):** https://snoop-staging.sallova.com
- **Branch:** `dev` — any push to `dev` auto-deploys to staging

#### Staging environment variables (Railway)
Staging mirrors production env vars with the following differences:

| Variable | Value | Notes |
|---|---|---|
| `ENV` | `staging` | Enables OTP bypass + test Twilio creds |
| `TWILIO_ACCOUNT_SID_TEST` | *(test SID)* | Used instead of real SID when `ENV=staging` |
| `TWILIO_AUTH_TOKEN_TEST` | *(test token)* | Used instead of real token when `ENV=staging` |
| `DATABASE_URL` | *(Railway Postgres — staging DB)* | Separate DB from production |

#### How staging differs from production
- **OTP bypass:** `ENV=staging` skips Twilio entirely — use code `0000` to verify any phone number
- **Test Twilio creds:** staging uses `TWILIO_ACCOUNT_SID_TEST` / `TWILIO_AUTH_TOKEN_TEST`
- **Separate database:** staging has its own Postgres instance on Railway
- **Vercel preview:** `VITE_API_URL` for Preview deployments points to the staging Railway backend

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

## Goodrec Auth

Goodrec uses **Firebase Auth** (project: `pickupsoccer-6a62a`) under the hood.

The snooper needs a Goodrec account's `access_token` and `refresh_token`. Since Goodrec uses Firebase email/password auth, you can get fresh tokens at any time via the Firebase REST API — no Proxyman needed:

```bash
curl -s -X POST \
  "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=<FIREBASE_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"email":"<your-goodrec-email>","password":"<your-goodrec-password>","returnSecureToken":true}'
```

Firebase API key is stored in Railway env vars as `FIREBASE_API_KEY`. The key value is documented in session memory (Dravon, 04/14/26).

Response contains:
- `idToken` → use as `access_token` (expires in 1 hour)
- `refreshToken` → use as `refresh_token` (long-lived)

### Seeding tokens into prod

Once you have fresh tokens, go to the **Admin dashboard → Tokens tab** and paste them in. No redeploy needed.

### How refresh works

The snooper checks the access token's expiry before each poll. If it's expiring within 2 minutes, it calls `_refresh_tokens()` in `services/goodrec.py` and saves the new tokens to the DB. Otherwise it uses the cached token directly. A `_refresh_tokens_firebase()` function also exists (not yet wired up) that refreshes directly via Firebase — this is the method the Goodrec mobile app uses and is the correct long-term approach.

If auth ever breaks (401s), you'll get a Slack alert with instructions to reseed.

---

## Testing SMS (Twilio verification)

Once Twilio has verified the account, use the test script to confirm real SMS delivery:

```bash
cd backend
source venv/bin/activate
python3 test_sms.py
```

`backend/test_sms.py` reads creds from `.env` and sends a real SMS to `+15713989671` using the prod Twilio account and phone number. It bypasses the `is_test_env` gate so it always hits the real Twilio API regardless of `ENV`.

---

## TODO
- [ ] Wire up real Goodrec API params in `services/goodrec.py`
- [ ] Add `TWILIO_FROM_NUMBER` to config + .env.example
- [ ] Set up Alembic migrations
- [ ] Add unsubscribe flow (reply STOP or settings page)
- [ ] Tighten CORS in production
- [ ] Deploy to DigitalOcean








