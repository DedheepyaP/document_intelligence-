# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    TORCHINDUCTOR_CACHE_DIR=/tmp/torchinductor_cache \
    HOME=/home/appuser

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    ffmpeg \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -u 1000 -m appuser \
    && mkdir -p /tmp/torchinductor_cache \
    && chown appuser:appuser /tmp/torchinductor_cache

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-interaction --no-ansi

COPY --chown=appuser:appuser . .

RUN chown -R appuser:appuser /home/appuser
# RUN mkdir -p /app/uploads \
#     && chown -R appuser:appuser /home/appuser /app/uploads

USER appuser

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]