# Docker image definition for Stage 0 scaffold.
FROM python:3.11-slim AS base
ENV POETRY_VERSION=1.8.3
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app
COPY pyproject.toml ./
RUN poetry install --no-interaction --no-root

COPY . .
RUN poetry install --no-interaction

CMD ["poetry", "run", "python", "-m", "app.bot.main"]
