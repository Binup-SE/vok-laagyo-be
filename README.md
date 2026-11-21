# Vok Laagyo API

Single Flask API + Postgres. Schema ownership lives **in this repo** (models + Alembic) — same workflow as Reg-1 db-manager, without a separate migrate service.

## Prerequisites

- Python 3.11+
- Local Postgres 17 (or Docker Compose via `docker-compose.yml`)

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Ensure .env exists with DATABASE_URL / FLASK_APP=run:app
```

Create DB/user once (or `scripts/setup_local_db.sql` as postgres superuser):

```sql
CREATE USER vok WITH PASSWORD 'vok';
CREATE DATABASE vok_laagyo OWNER vok;
```

Then:

```powershell
flask db upgrade
# or: python scripts/db_upgrade.py
flask run -p 5000
```

```powershell
curl http://127.0.0.1:5000/api/v1/health
```

## Database workflow (add a table)

Structured like Reg-1 db-manager:

1. **Model** — add/edit under `app/models/`  
   - Subclass `BaseModel` (UUID + `date_added` / `date_updated` / `added_by` / `updated_by`)
2. **Export** — import the model in `app/models/__init__.py`
3. **Migrate**
   ```powershell
   flask db migrate -m "add clients table"
   flask db upgrade
   ```

| Concern | Location |
|---------|----------|
| Models | `app/models/` (`base.py`, `client.py`, …) |
| Revisions | `migrations/versions/` |
| One-shot upgrade | `python scripts/db_upgrade.py` |

Avoid `flask db stamp head` as normal setup (Reg-1 habit). Prefer real upgrades from revision 0.

## `app/common` helpers

| Module | Use |
|--------|-----|
| `app.common.db` | session helpers, Postgres pool options |
| `app.common.response` | `{ success, data }` / `{ success, key, message }` |
| `app.common.exceptions` | `AppError` subclasses |
