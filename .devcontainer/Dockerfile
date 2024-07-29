FROM mcr.microsoft.com/devcontainers/python:3.12

COPY requirements.txt .

COPY scripts/download_model.py .

RUN pip install -r requirements.txt && \
    python download_model.py
