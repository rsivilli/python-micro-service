ARG FUNCTION_DIR="/code"

FROM python:3.10 AS build-image
ARG FUNCTION_DIR

RUN mkdir -p ${FUNCTION_DIR}



ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=2.0.0
  # ^^^
  # Make sure to update it!

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -


WORKDIR ${FUNCTION_DIR}
COPY pyproject.toml poetry.lock README.md ./
RUN mkdir -p ./src
RUN poetry install --no-root

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini api_handler.py migrations_handler.py ./


CMD ["/usr/local/bin/python", "-m","uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
