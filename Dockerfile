FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.1.13 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

WORKDIR /app

RUN pip install poetry=="$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-ansi

COPY . .

COPY ./scripts/* /scripts/

RUN chmod +x -R /scripts
