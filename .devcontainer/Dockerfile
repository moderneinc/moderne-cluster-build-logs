FROM mcr.microsoft.com/devcontainers/python:3.12 AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

FROM base AS dependencies
WORKDIR /app
COPY pyproject.toml .
RUN uv pip install --system -r pyproject.toml

FROM dependencies AS application
COPY scripts/download_model.py .

FROM application AS models
RUN uv run download_model.py

FROM models AS final
COPY scripts/* .

RUN chmod +x entry-point.sh
ENTRYPOINT ["./entry-point.sh"]