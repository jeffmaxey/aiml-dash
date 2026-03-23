# syntax=docker/dockerfile:1.7

FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        build-essential \
        gcc \
        unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock README.md /app/
RUN uv sync --frozen --no-dev --no-editable --no-install-project

COPY aiml_dash /app/aiml_dash
RUN uv sync --frozen --no-dev --no-editable


FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    AIML_DASH_ENVIRONMENT=production \
    AIML_DASH_DEBUG=false \
    AIML_DASH_HOST=0.0.0.0 \
    AIML_DASH_PORT=8050 \
    GUNICORN_CMD_ARGS="--bind 0.0.0.0:8050 --workers 2 --threads 4 --timeout 120 --access-logfile - --error-logfile -" \
    PATH=/app/.venv/bin:$PATH

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        ca-certificates \
        curl \
        tini \
        unixodbc \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system appuser \
    && useradd --system --gid appuser --create-home --home-dir /home/appuser appuser

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/aiml_dash /app/aiml_dash
COPY pyproject.toml README.md /app/

RUN mkdir -p /app/.aiml_dash \
    && chown -R appuser:appuser /app /home/appuser

USER appuser

EXPOSE 8050

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"AIML_DASH_PORT\", \"8050\")}/', timeout=3)"

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["gunicorn", "aiml_dash:server"]
