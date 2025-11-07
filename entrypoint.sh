#!/bin/bash
set -e  # Exit immediately if a command fails

# Create DB if not exists
python /app/init_db.py

# Navigate to app directory
cd /app

<<<<<<< HEAD
# echo "Starting Alembic migrations..."

# # Automatically create a revision if needed (optional)
# # This will generate a new migration for any detected model changes
# # Comment out if you only want manual revisions
# alembic revision --autogenerate -m "auto revision" || echo "No changes detected"

# # Apply all migrations
# alembic upgrade head

# echo "Migrations applied successfully."
=======
echo "Starting Alembic migrations..."

# Automatically create a revision if needed (optional)
# This will generate a new migration for any detected model changes
# Comment out if you only want manual revisions
alembic revision --autogenerate -m "auto revision" || echo "No changes detected"

# Apply all migrations
alembic upgrade head

echo "Migrations applied successfully."
>>>>>>> main

# Launch FastAPI with Gunicorn + Uvicorn workers
# - 4 workers (adjust as needed)
# - bind to all interfaces on port 8000

exec gunicorn src.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120

# exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload