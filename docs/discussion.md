# Vok Laagyo — project decisions

Single brief of decisions so far. Full tenancy detail lives in [multi-tenant-architecture.md](./multi-tenant-architecture.md); this file is the opinionated summary.

---

## 1. Product goal

Multi-tenant digital menu (feeme.cc-like): many restaurants, one product surface — public QR/menu + admin CRUD — on **one shared Next.js app**, **one shared Flask API**, **one shared Postgres database**.

---

## 2. Stack

| Layer      | Choice                                                                   |
| ---------- | ------------------------------------------------------------------------ |
| Frontend   | Next.js (one build; branding from API)                                   |
| API        | One Flask app (not Reg-1 user-api + shared-api)                          |
| DB         | Postgres (shared schema + `tenant_id` + RLS)                             |
| Migrations | Alembic / Flask-Migrate **inside the Flask API**                         |
| Early cost | $0 local Postgres (Docker / apt / Homebrew); free hosted later if needed |

---

## 3. Tenancy model (summary)

**Default:** shared DB + shared schema + row-level `tenant_id` on every tenant-owned table. Not DB-per-tenant / schema-per-tenant for this product.

| Concern         | Decision                                                                                 |
| --------------- | ---------------------------------------------------------------------------------------- |
| Public identity | Subdomain primary (`slug`); custom domain optional; path `/m/:slug` fallback only        |
| Resolve once    | Host → `tenant_id` → thread through auth and queries                                     |
| Trust           | Never trust client-supplied `tenant_id` (query/body); 404 unknown hosts in prod          |
| Admin           | Same tenant host + session bound to `user_id` + `tenant_id` via `memberships`            |
| Enforcement     | App-layer scoping mandatory; Postgres RLS + pool `SET LOCAL` / reset as defense-in-depth |
| Branding        | One FE build; per-tenant theme/logo from `tenant_settings` API                           |

Full model, tables, Flask/Next patterns, seeds, and phased rules: **[multi-tenant-architecture.md](./multi-tenant-architecture.md)**.

---

## 4. Reg-1 reference (copy / invent / avoid)

Six Reg-1 extracts (architecture, tenancy, auth, data/media, FE–BE/deploy, gap analysis) were reviewed **2026-11-08** — **enough as an architecture reference**. They do **not** replace Vok’s multi-tenant doc for schema or RLS.

### Copy

- Host / subdomain as the primary tenant signal
- Seal tenant into the **admin session** at login; BFF injects token + tenant
- Hard fail on missing token / missing tenant
- Tenant-prefixed object storage + short-lived signed URLs
- One Next deployment, many hosts
- Public shell vs admin shell split

### Invent (Reg-1 won’t give these)

- `tenants` / `tenant_domains` / global `users` / `memberships`
- Row-level `tenant_id` everywhere + RLS + pool session vars
- JWT/session claim `tenant_id` checked against Host-resolved tenant
- `tenant_settings.theme_json` white-label
- Public menu that trusts **Host only** (no `?tenant=` as primary)
- Single Flask + single Postgres; menu/categories/items schema from Vok’s architecture doc

### Avoid

- DB-per-customer / SQLAlchemy bind maps as the product default
- JWT without `tenant_id`; API trusting `X-Tenant-Id` alone
- Public `?tenant=` / path as production primary identity
- Exposing backend access tokens to the browser when BFF-only is enough
- Separate DB-manager repo + `db stamp head` / multi-service migrate dances as normal flow
- Reg-1’s user-api + shared-api + microservice mesh

**Non-blocking open questions** from Reg-1 (KV bind runbook, gateway tenant checks, cross-DB emails, MySQL→Postgres parity) — fine to start phases 1–2 without them.

Reusable extract prompt: [reference-app-architecture-prompt.md](./reference-app-architecture-prompt.md).

---

## 5. Build order

**Backend first.** Thin Next Host→API stub in parallel is OK; do **not** lead with menu UI.

1. Postgres: `tenants` + `tenant_domains` + slug uniqueness
2. Flask: Host → `g.tenant` (404 unknown)
3. `users` + `memberships` + session with `tenant_id`
4. First tenant-scoped resource + RLS
5. Public read API + Tenant A/B isolation tests
6. Admin CRUD + roles (`owner` \| `manager` \| `staff`)
7. Next: middleware / Host resolve + public SSR menu + admin
8. Then categories, media, settings/theme, custom domains, orders

---

## 6. Repo layout

| Option                                    | Verdict                                                    |
| ----------------------------------------- | ---------------------------------------------------------- |
| **Monorepo** (`apps/web` + `apps/api`)    | **Preferred day one** — one Compose, one vertical-slice PR |
| FE repo + BE repo                         | **Acceptable** — still **one** Flask API                   |
| Reg-1-style user / shared / FE multi-repo | **No**                                                     |

**This repo (BE):** Flask API at the repo root (`app/`, `migrations/`, `run.py`). Don’t let repo topology delay tenants + Host resolve work.

---

## 7. DB choice, $0 local, bootstrap / migrations

- **Stay on Postgres** — matches shared schema, `tenant_id`, and RLS. Skip SQLite and MySQL for the core path.
- **Starting phase:** local Postgres only ($0). Optional Compose via root `docker-compose.yml`; free hosted (Neon / Supabase / etc.) when a remote env is actually needed.
- **Bootstrap:** `CREATE DATABASE vok_laagyo` (or equivalent) directly in Postgres — empty DB, then migrate forward from revision 0.
- **Migrations live in the Flask API** at [`migrations/`](../migrations/) (Flask-Migrate / Alembic). That app owns models + revisions.
- **No separate database-manager for MVP** — do not put schema ownership in a separate package/repo.
- **Avoid:** Reg-1 `db stamp head` as normal setup; multi-service migrate ownership fights; infra/KV bind provisioning as the product tenancy model.

---

## 8. Related docs

| Doc                                                                            | Role                                                               |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| [multi-tenant-architecture.md](./multi-tenant-architecture.md)                 | Full tenancy model, schema sketch, Flask/Next rules, seeds, phases |
| [reference-app-architecture-prompt.md](./reference-app-architecture-prompt.md) | Copy-paste prompt to extract architecture from a reference app     |
| [project-context.md](./project-context.md)                                     | Short index into this Project’s docs                               |
| This file                                                                      | Consolidated decisions brief                                       |
