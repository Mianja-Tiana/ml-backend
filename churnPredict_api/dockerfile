# # Base image with Python
# FROM python:3.11-slim

# # Set environment variables
# ENV PYTHONUNBUFFERED=1 \
#     POETRY_VIRTUALENVS_CREATE=false \
#     PIP_NO_CACHE_DIR=1

# # Set working directory
# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libpq-dev \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements (or pyproject.toml if using Poetry)
# COPY requirements.txt .

# # Install Python dependencies
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt

# # Copy only app source code and alembic folder
# COPY src/ /app/src/
# COPY alembic/ /app/alembic/
# COPY alembic.ini /app/alembic.ini

# # Set PYTHONPATH so imports work correctly
# ENV PYTHONPATH=/app/src:${PYTHONPATH:-}


# # Expose the port FastAPI will run on
# EXPOSE 8000

# # Copy entrypoint script
# COPY entrypoint.sh /entrypoint.sh
# RUN chmod +x /entrypoint.sh

# # Start the app using Uvicorn
# ENTRYPOINT ["/entrypoint.sh"]



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

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
