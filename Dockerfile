FROM python:3.14-slim AS base

ENV PATH="${PATH}:/root/.local/bin" \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off \
    PORT=8000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.2.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR="/var/cache/pypoetry"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && curl -sSL --compressed "https://install.python-poetry.org" | python3 \
    && apt purge --autoremove -y curl build-essential \
    && apt clean -y \
    && rm -rf /var/lib/apt/lists/* /root/.cache

WORKDIR /project
COPY pyproject.toml ./

EXPOSE ${PORT}

FROM base AS develop

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && poetry install --no-root \
    && apt purge --autoremove -y build-essential \
    && apt clean -y \
    && rm -rf /var/lib/apt/lists/* /root/.cache "${POETRY_CACHE_DIR}"

COPY . .

CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:${PORT}"]

FROM base AS production

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && poetry install --only main --no-root \
    && apt purge --autoremove -y build-essential \
    && apt clean -y \
    && rm -rf /var/lib/apt/lists/* /root/.cache "${POETRY_CACHE_DIR}"

COPY . .

CMD ["uwsgi", "./car_parking/uwsgi.ini"]
