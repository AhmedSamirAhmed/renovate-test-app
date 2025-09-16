FROM python:3.13-alpine AS base

COPY pyproject.toml poetry.lock ./

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN poetry install --no-root --only main

COPY app.py config.default.ini ./

EXPOSE 8080

CMD ["/app/.venv/bin/python", "app.py"]
