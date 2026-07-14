# Database Indexes — TODO

The current SQLAlchemy models don't define indexes beyond PKs and the `unique=True` on `users.phone`. As user count grows, the poller (runs every 15 min) will start doing full table scans on hot query paths.

## Indexes to Add

### `user_preferences`
```sql
CREATE INDEX IF NOT EXISTS ix_user_preferences_venue_key ON user_preferences(venue_key);
CREATE INDEX IF NOT EXISTS ix_user_preferences_user_id ON user_preferences(user_id);
```
**Why:** The poller joins `users` → `user_preferences` filtering by `venue_key` on every run. Without an index this is a full scan. `user_id` is a FK — Postgres doesn't auto-index FKs.

### `users`
```sql
CREATE INDEX IF NOT EXISTS ix_users_verified ON users(verified);
```
**Why:** Every poller query filters `WHERE verified = TRUE`. Low cardinality but still worth it as the user table grows.

### `user_notified_events`
Already covered — `(user_id, event_id)` is a composite PK, so Postgres indexes it automatically.

---

## How to Apply

### 1. Update the SQLAlchemy models (`backend/app/db/models.py`)

Add `index=True` to the relevant columns:

```python
# UserPreference
venue_key: Mapped[str] = mapped_column(String, nullable=False, index=True)
user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)

# User
verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
```

This ensures future environments created via `create_all()` get the indexes automatically.

### 2. Apply manually to existing DBs

Since we're not using Alembic, the indexes need to be run manually on staging and prod:

```bash
# Staging
psql "postgresql://postgres:<pass>@interchange.proxy.rlwy.net:15262/railway" -c "
CREATE INDEX IF NOT EXISTS ix_user_preferences_venue_key ON user_preferences(venue_key);
CREATE INDEX IF NOT EXISTS ix_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS ix_users_verified ON users(verified);
"

# Production
psql "postgresql://postgres:<pass>@maglev.proxy.rlwy.net:59095/railway" -c "
CREATE INDEX IF NOT EXISTS ix_user_preferences_venue_key ON user_preferences(venue_key);
CREATE INDEX IF NOT EXISTS ix_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS ix_users_verified ON users(verified);
"
```

Get the passwords from Railway env vars (`DATABASE_PUBLIC_URL`).

---

## Priority

Low — at current scale this won't matter. Worth doing once user count gets into the hundreds or the poller starts logging slow queries.
