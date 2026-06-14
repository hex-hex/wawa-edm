# wawa-edm

<p align="center">
  <img src="static/img/logo.svg" alt="Wawa EDM logo" width="560">
</p>

A Django REST backend for a lightweight **EDM** (email direct marketing) / CRM workflow.
It manages companies, contacts, reusable knowledge snippets, email tasks (campaigns), and
email drafts — exposing full CRUD REST APIs and a Django admin with rendered Markdown/HTML
previews.

## Features

- **REST API** (Django REST Framework) with CRUD for every resource, pagination, `?search=`,
  and exact filtering on enum fields (e.g. `?status=`).
- **Django admin** for all models, with read-only **Markdown/HTML previews** of long-form
  content fields (sanitized with `nh3`).
- **UUID primary keys** and `created_at` / `updated_at` timestamps on every model.
- Served over **ASGI** (Uvicorn); static files via **WhiteNoise**.
- **PostgreSQL** storage and **Redis** cache, configured from the environment (`.env`).
- Reproducible tooling with **uv**; containerized with a **Dockerfile** + **docker-compose**.

## Tech stack

| Area | Choice |
|------|--------|
| Language / runtime | Python 3.13+ (managed by `uv`) |
| Framework | Django 6.0 |
| API | Django REST Framework |
| ASGI server | Uvicorn |
| Static files | WhiteNoise |
| Database | PostgreSQL (via `psycopg` 3) |
| Cache | Redis (via `django-redis`) |
| Config | `django-environ` (`.env`) |
| Filtering | `django-filter` (exact / enum) |
| Rendering | `markdown` + `nh3` (sanitizer) |

## Data model

All models live in the `core` app. UUID PKs + timestamps throughout.

| Model | Fields | Relationships |
|-------|--------|---------------|
| `Company` | `name`, `website`, `address`, `about` (markdown) | — |
| `Contact` | `first_name`, `middle_name`, `last_name`, `email`, `role`, `phone`, `priority` (enum), `gender` (enum), `behavior` (markdown), `story` (markdown) | `company` → `Company` |
| `Knowledge` | `abstract`, `content` (markdown) | — |
| `EmailTask` | `name`, `target`, `strategy` | `knowledges` ⇄ `Knowledge` (M2M) |
| `EmailDraft` | `title`, `pain_points` (markdown), `content` (HTML), `status`, `version` | `contact` → `Contact`, `task` → `EmailTask` |

Relationships: `Company` 1—∗ `Contact` 1—∗ `EmailDraft`; `EmailTask` 1—∗ `EmailDraft`
(the task that guided the draft); `EmailTask` ∗—∗ `Knowledge`.
`EmailDraft.status` is one of `draft` (default) / `scheduled` / `sent` / `failed`.
`Contact.priority` is one of `hot` / `warm` / `cold` and `Contact.gender` is one of
`male` / `female` / `other`. `middle_name`, `email`, `role`, `phone`, `priority`, `gender`,
and `behavior` are all optional.

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

**Filtering** — enum fields support exact-match query params (via `django-filter`):

```
GET /api/email-drafts/?status=draft        # exact match: draft | scheduled | sent | failed
GET /api/email-drafts/?status=sent&search=welcome   # combine with ?search=
GET /api/contacts/?priority=hot            # exact match: hot | warm | cold
GET /api/contacts/?gender=female           # exact match: male | female | other
GET /api/email-drafts/?task=<uuid>         # drafts written under a given EmailTask
```

An invalid value (e.g. `?status=bogus`) returns `400`.

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

# 6. Run the dev server
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

The image builds a runnable app (deps via `uv`, static collected, served by Uvicorn); the
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

`Company.about`, `Contact.story`, `Knowledge.content`, and `EmailDraft.pain_points` render as
**Markdown**; `EmailDraft.content` renders as **HTML**. These fields are shown read-only (the
raw editor is hidden) via the reusable helper in [`core/admin_render.py`](core/admin_render.py).
Because the underlying fields are writable through the public API, all rendered output is
sanitized with `nh3` to prevent stored XSS in the admin.

## Brand assets

The Wawa EDM mark combines an envelope, a W-shaped message wave, and a send spark. Source SVGs
and ready-to-use raster exports live in [`static/img/`](static/img/).

| Asset | Purpose |
|-------|---------|
| [`logo.svg`](static/img/logo.svg) | Preferred scalable wordmark |
| [`logo.png`](static/img/logo.png) | Transparent PNG wordmark |
| [`favicon.svg`](static/img/favicon.svg) | Preferred scalable browser icon |
| [`favicon.ico`](static/img/favicon.ico) | Multi-size legacy browser icon |
| [`favicon-32x32.png`](static/img/favicon-32x32.png) | Standard browser favicon |
| [`favicon-192x192.png`](static/img/favicon-192x192.png) | Android / PWA icon |
| [`favicon-512x512.png`](static/img/favicon-512x512.png) | High-resolution app icon |

The project-level `static/` directory is registered through `STATICFILES_DIRS`, so Django and
`collectstatic` can discover these assets. In a Django template:

```django
{% load static %}

<link rel="icon" href="{% static 'img/favicon.ico' %}" sizes="any">
<link rel="icon" href="{% static 'img/favicon.svg' %}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{% static 'img/favicon-192x192.png' %}">

<img src="{% static 'img/logo.svg' %}" alt="Wawa EDM">
```

## Project structure

```
wawa-edm/
├── config/              # Django project (settings, urls, asgi/wsgi)
├── core/                # app: models, serializers, views, urls, admin
│   ├── admin_render.py  # reusable Markdown/HTML preview component
│   └── migrations/
├── static/
│   └── img/             # logo and favicon assets
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
