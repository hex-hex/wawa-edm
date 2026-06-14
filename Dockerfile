# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Bring in the uv binary (matches the version used locally).
COPY --from=ghcr.io/astral-sh/uv:0.9.8 /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install dependencies first so this layer is cached across code changes.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy the application source.
COPY . .

# Collect static assets (whitenoise serves them at runtime). Uses settings'
# built-in defaults; no DB/Redis connection happens here.
RUN python manage.py collectstatic --noinput \
    && chmod +x docker-entrypoint.sh

EXPOSE 8000

# Entrypoint runs migrations, then execs the CMD (uvicorn ASGI server).
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
