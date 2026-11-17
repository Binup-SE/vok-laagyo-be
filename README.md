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
flask seed
flask run -p 5000
```

Dev seed owners (password for both: `password`):

- `owner@cafe-roma.test` → cafe-roma  
- `owner@spice-house.test` → spice-house  

## Database workflow (add a table)

Structured like Reg-1 db-manager:

1. **Model** — add/edit under `app/models/`  
   - Platform tables: subclass `BaseModel` (UUID + `created_at`)  
   - Tenant-owned tables: subclass `TenantBaseModel` (adds `tenant_id`)
2. **Export** — import the model in `app/models/__init__.py`
3. **Migrate**
   ```powershell
   flask db migrate -m "add users table"
   flask db upgrade
   ```
4. **Seed** (optional)
   ```powershell
   flask seed
   ```

| Concern | Location |
|---------|----------|
| Models | `app/models/` (`base.py`, `tenant.py`, …) |
| Revisions | `migrations/versions/` |
| Seeds | `seeds/` + `flask seed` |
| One-shot upgrade | `python scripts/db_upgrade.py` |

Avoid `flask db stamp head` as normal setup (Reg-1 habit). Prefer real upgrades from revision 0.

## Tenant resolution

Host only (never client `tenant_id`):

1. `tenant_domains.hostname`
2. Subdomain of `BASE_DOMAIN` → `tenants.slug`
3. Dev path `/m/:slug` when `ALLOW_PATH_TENANT=1`

```powershell
curl http://127.0.0.1:5000/api/v1/health
curl -H "Host: cafe-roma.voklaagyo.localhost" http://127.0.0.1:5000/api/v1/tenant
```

## Auth (user-api patterns, Vok-safe)

Copied ideas: `X-Access-Token` (or `Authorization: Bearer`), keyed errors, login decorator.  
**Fixed vs user-api:** JWT claims include `user_id` + `tenant_id` + `role`, and must match Host → `g.tenant`.

```powershell
# Login (Host selects tenant)
curl -X POST http://127.0.0.1:5000/api/v1/auth/login `
  -H "Host: cafe-roma.voklaagyo.localhost" `
  -H "Content-Type: application/json" `
  -d "{\"email\":\"owner@cafe-roma.test\",\"password\":\"password\"}"

# Me
curl http://127.0.0.1:5000/api/v1/auth/me `
  -H "Host: cafe-roma.voklaagyo.localhost" `
  -H "X-Access-Token: <token>"
```

Protect routes with `@authenticate_request` or `@require_roles("owner", "manager")` from `app.common.auth`.

## `app/common` helpers

| Module | Use |
|--------|-----|
| `app.common.db` | session helpers, Postgres pool options, RLS GUC hooks |
| `app.common.response` | `{ success, data }` / `{ success, key, message }` |
| `app.common.exceptions` | `AppError` subclasses (`UNKNOWN_TENANT`, `MISSING_TOKEN`, …) |
| `app.common.auth` | password hash, JWT mint/verify, `authenticate_request` |
