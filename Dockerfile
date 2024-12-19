FROM mcr.microsoft.com/devcontainers/python:3.12 AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

FROM base AS dependencies
COPY pyproject.toml .
COPY uv.lock .
RUN uv pip install --system -r pyproject.toml

FROM dependencies AS models
COPY scripts/download_model.py .
RUN uv run download_model.py

FROM models AS final
COPY scripts/* .
COPY templates templates
