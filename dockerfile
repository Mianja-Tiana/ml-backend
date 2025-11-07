<<<<<<< HEAD
# Builder stage
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

COPY src/ /app/src/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/alembic.ini


# Final stage
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src:${PYTHONPATH:-}

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --from=builder /app/src /app/src
COPY --from=builder /app/alembic /app/alembic
COPY --from=builder /app/alembic.ini /app/alembic.ini

COPY init_db.py /app/init_db.py

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Add user and assign ownership
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

=======
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src


RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
>>>>>>> main
USER appuser

EXPOSE 8000

<<<<<<< HEAD
ENTRYPOINT ["/entrypoint.sh"]
=======
>>>>>>> main
