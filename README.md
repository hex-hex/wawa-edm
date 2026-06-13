# wawa-edm

A Django REST backend for a lightweight **EDM** (email direct marketing) / CRM workflow.
It manages companies, contacts, reusable knowledge snippets, email tasks (campaigns), and
email drafts — exposing full CRUD REST APIs and a Django admin with rendered Markdown/HTML
previews.

## Features

- **REST API** (Django REST Framework) with CRUD for every resource, pagination, and `?search=`.
- **Django admin** for all models, with read-only **Markdown/HTML previews** of long-form
  content fields (sanitized with `nh3`).
- **UUID primary keys** and `created_at` / `updated_at` timestamps on every model.
- Served over **ASGI** (Daphne); static files via **WhiteNoise**.
- **PostgreSQL** storage and **Redis** cache, configured from the environment (`.env`).
- Reproducible tooling with **uv**; containerized with a **Dockerfile** + **docker-compose**.

## Tech stack

| Area | Choice |
|------|--------|
| Language / runtime | Python 3.13+ (managed by `uv`) |
| Framework | Django 6.0 |
| API | Django REST Framework |
| ASGI server | Daphne |
| Static files | WhiteNoise |
| Database | PostgreSQL (via `psycopg` 3) |
| Cache | Redis (via `django-redis`) |
| Config | `django-environ` (`.env`) |
| Rendering | `markdown` + `nh3` (sanitizer) |

## Data model

All models live in the `core` app. UUID PKs + timestamps throughout.

| Model | Fields | Relationships |
|-------|--------|---------------|
| `Company` | `name`, `about` (markdown) | — |
| `Contact` | `first_name`, `last_name`, `email`, `story` (markdown) | `company` → `Company` |
| `Knowledge` | `abstract`, `content` (markdown) | — |
| `EmailTask` | `name`, `target`, `strategy` | `knowledges` ⇄ `Knowledge` (M2M) |
| `EmailDraft` | `title`, `content` (HTML), `status`, `version` | `contact` → `Contact` |

Relationships: `Company` 1—∗ `Contact` 1—∗ `EmailDraft`; `EmailTask` ∗—∗ `Knowledge`.
`EmailDraft.status` is one of `draft` (default) / `scheduled` / `sent` / `failed`.

## API

Base path: `/api/` (browsable API enabled in DEBUG). All endpoints support
`GET` (list/retrieve), `POST`, `PUT`, `PATCH`, `DELETE` and `?search=`.

| Resource | Endpoint |
|----------|----------|
| Companies | `/api/companies/` |
| Contacts | `/api/contacts/` |
| Knowledge | `/api/knowledge/` |
| Email tasks | `/api/email-tasks/` |
| Email drafts | `/api/email-drafts/` |

Admin: `/admin/`.

## Requirements

- [uv](https://docs.astral.sh/uv/) (it installs the right Python automatically)
- A local **PostgreSQL** server and **Redis** server

> The reference setup runs Postgres and Redis as local Docker containers published on
> `127.0.0.1:5432` and `127.0.0.1:6379`; any local instances work.

## Getting started (local development)

```bash
# 1. Install dependencies (creates .venv with the pinned Python)
uv sync

# 2. Configure the environment
cp .env.example .env          # then edit secrets / connection URLs as needed

# 3. Create the database (defaults to user/pass postgres/postgres)
psql -h 127.0.0.1 -U postgres -c "CREATE DATABASE wawa_edm;"

# 4. Apply migrations
uv run python manage.py migrate

# 5. Create an admin user
uv run python manage.py createsuperuser

# 6. Run the dev server (Daphne / ASGI)
uv run python manage.py runserver
```

The app is then at <http://localhost:8000/> — API under `/api/`, admin under `/admin/`.

### Environment variables

Read from `.env` (see [`.env.example`](.env.example)):

| Key | Description | Local default |
|-----|-------------|---------------|
| `DJANGO_SECRET_KEY` | Django secret key | insecure dev key |
| `DJANGO_DEBUG` | Debug mode (`True`/`False`) | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | Postgres connection URL | `postgres://postgres:postgres@127.0.0.1:5432/wawa_edm` |
| `REDIS_URL` | Redis connection URL | `redis://127.0.0.1:6379/1` |

## Running with Docker

The image builds a runnable app (deps via `uv`, static collected, served by Daphne); the
entrypoint runs migrations on startup. `docker-compose.yml` reuses the host's Postgres/Redis
via `host.docker.internal`.

```bash
docker compose up -d --build      # build and start
docker compose logs -f            # follow logs
docker compose down               # stop
```

The service is published on **host port 8010** → <http://localhost:8010/>
(host `8000` was in use in the reference environment; change the `ports` mapping in
`docker-compose.yml` if you prefer `8000`). Override `DATABASE_URL` / `REDIS_URL` in the
compose `environment` block to point at a different database or cache.

## Admin previews

`Company.about`, `Contact.story`, and `Knowledge.content` render as **Markdown**;
`EmailDraft.content` renders as **HTML**. These fields are shown read-only (the raw editor is
hidden) via the reusable helper in [`core/admin_render.py`](core/admin_render.py). Because the
underlying fields are writable through the public API, all rendered output is sanitized with
`nh3` to prevent stored XSS in the admin.

## Project structure

```
wawa-edm/
├── config/              # Django project (settings, urls, asgi/wsgi)
├── core/                # app: models, serializers, views, urls, admin
│   ├── admin_render.py  # reusable Markdown/HTML preview component
│   └── migrations/
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── pyproject.toml       # dependencies (managed by uv)
```

## Useful commands

```bash
uv run python manage.py check            # system checks
uv run python manage.py makemigrations   # create migrations after model changes
uv run python manage.py migrate          # apply migrations
uv run python manage.py createsuperuser  # add an admin user
uv run python manage.py shell            # Django shell
```
