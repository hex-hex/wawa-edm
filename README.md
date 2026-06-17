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
| `Contact` | `first_name`\*, `middle_name`\*, `last_name`\*, `email`\*, `role`\*, `phone`\*, `priority`\* (enum), `gender`\* (enum), `behavior`\* (markdown), `story` (markdown) | `company` → `Company` |
| `KnowledgeTag` | `name` (unique, max 127 chars) | — |
| `Knowledge` | `abstract`, `content` (markdown) | `tags` ⇄ `KnowledgeTag` (M2M) |
| `EmailTask` | `name`, `target`, `strategy` | `knowledges` ⇄ `Knowledge` (M2M) |
| `EmailDraft` | `subject`, `pain_points` (markdown), `content` (HTML), `status`, `version` | `contact` → `Contact`, `task` → `EmailTask`, `knowledges` ⇄ `Knowledge` (M2M) |

Relationships: `Company` 1—∗ `Contact` 1—∗ `EmailDraft`; `EmailTask` 1—∗ `EmailDraft`
(the task that guided the draft); `EmailTask` ∗—∗ `Knowledge`; `EmailDraft` ∗—∗ `Knowledge`;
`Knowledge` ∗—∗ `KnowledgeTag`.
`EmailDraft.status` is one of `draft` (default) / `scheduled` / `sent` / `failed`.
`Contact.priority` is one of `hot` / `warm` / `cold` and `Contact.gender` is one of
`male` / `female` / `other`. Fields marked \* are optional on `Contact`; only `company`
and `story` are required.

## API

Base path: `/api/` (browsable API enabled in DEBUG). All endpoints support
`GET` (list/retrieve), `POST`, `PUT`, `PATCH`, `DELETE` and `?search=`.

| Resource | Endpoint |
|----------|----------|
| Companies | `/api/companies/` |
| Contacts | `/api/contacts/` |
| Knowledge tags | `/api/knowledge-tags/` |
| Knowledge | `/api/knowledge/` |
| Knowledge abstracts | `/api/knowledge/abstract/` |
| Email tasks | `/api/email-tasks/` |
| Email drafts | `/api/email-drafts/` |

**Filtering** — enum fields and relations support exact-match query params (via `django-filter`):

```
GET /api/email-drafts/?status=draft               # exact match: draft | scheduled | sent | failed
GET /api/email-drafts/?status=sent&search=welcome # combine with ?search=
GET /api/contacts/?priority=hot                   # exact match: hot | warm | cold
GET /api/contacts/?gender=female                  # exact match: male | female | other
GET /api/companies/?about_empty=true              # companies whose about is null or blank
GET /api/contacts/?story_empty=true               # contacts whose story is null or blank
GET /api/email-drafts/?task=<uuid>                # drafts written under a given EmailTask
GET /api/email-drafts/?task_latest=<uuid>         # latest-version draft per contact under a given EmailTask
GET /api/email-drafts/?knowledges=<uuid>          # drafts associated with a specific Knowledge snippet
GET /api/knowledge/abstract/?search=产品          # compact id + abstract list for LLM selection
GET /api/knowledge/abstract/?tags=<uuid>          # compact abstracts filtered by tag id
GET /api/knowledge/abstract/?tags__name=产品       # compact abstracts filtered by exact tag name
GET /api/knowledge/?tags=<uuid>                   # knowledge with a specific tag (by id)
GET /api/knowledge/?tags__name=产品               # knowledge with a specific tag (by exact name)
GET /api/knowledge/?tags__name__icontains=产      # knowledge with a tag name containing substring
```

The boolean `about_empty` / `story_empty` filters treat a field as empty when it is `NULL`
**or** an empty string (`""`). Use `=true` for missing/blank values and `=false` for records
that have content — handy for finding records that still need enrichment.
The `task_latest` filter mirrors the admin task filter: for the selected task, it returns
only the highest `version` `EmailDraft` for each contact.

**Knowledge tag usage:**

```
# Create a tag
POST /api/knowledge-tags/
{"name": "产品介绍"}

# List all tags
GET /api/knowledge-tags/

# List compact knowledge abstracts for LLM selection
GET /api/knowledge/abstract/
[{"id": "<knowledge-uuid>", "abstract": "..."}]

# Narrow compact abstracts by tag, tag name, or search text
GET /api/knowledge/abstract/?tags=<tag-uuid>
GET /api/knowledge/abstract/?tags__name=产品介绍
GET /api/knowledge/abstract/?tags__name__icontains=产品&search=pricing

# Attach tags to a knowledge snippet (pass a list of tag UUIDs)
POST /api/knowledge/
{"abstract": "...", "content": "...", "tags": ["<tag-uuid>", "<tag-uuid-2>"]}

# Update tags on an existing snippet
PATCH /api/knowledge/<uuid>/
{"tags": ["<tag-uuid>"]}

# Create or update an email draft with associated knowledge snippets
POST /api/email-drafts/
{"contact": "<contact-uuid>", "task": "<task-uuid>", "subject": "...", "version": 1, "knowledge_ids": ["<knowledge-uuid>"]}

PATCH /api/email-drafts/<uuid>/
{"knowledge_ids": ["<knowledge-uuid>", "<knowledge-uuid-2>"]}

# Filter knowledge by tag
GET /api/knowledge/?tags__name=产品介绍
```

The response for each knowledge snippet includes both `tags` (list of UUIDs, writable) and
`tag_names` (list of name strings, read-only).
Email tasks accept `knowledges` as UUIDs on write and return full nested knowledge objects
on read. Email drafts return nested `knowledges` on read and use `knowledge_ids` for
POST/PATCH updates.

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

Set in the `environment` block of `docker-compose.yml`:

| Key | Description | Default in compose |
|-----|-------------|--------------------|
| `DJANGO_SECRET_KEY` | Django secret key | (set explicitly) |
| `DJANGO_DEBUG` | Debug mode (`True`/`False`) | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` (+ your domain) |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins for CSRF | `https://your-domain.example` |
| `DATABASE_URL` | Postgres connection URL | via `host.docker.internal` |
| `REDIS_URL` | Redis connection URL | via `host.docker.internal` |
| `API_ALLOWED_IPS` | CIDRs allowed to call the REST API | Docker / LAN / Tailscale ranges |
| `TRUSTED_PROXIES` | CIDRs of trusted reverse proxies (XFF) | same as `API_ALLOWED_IPS` |

## Running with Docker

The image builds a runnable app (deps via `uv`, static collected, served by Uvicorn); the
entrypoint runs migrations on startup. `docker-compose.yml` reuses the host's Postgres/Redis
via `host.docker.internal`.

```bash
docker compose up -d --build      # build and start
docker compose logs -f            # follow logs
docker compose down               # stop
```

The service is published on **host port 8030** → <http://localhost:8030/>.
All environment variables are set directly in the `environment` block of `docker-compose.yml` —
no `.env` file is used. Override `DATABASE_URL` / `REDIS_URL` there to point at a different
database or cache.

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
