#!/bin/bash
# Development server startup script

# Activate virtual environment
source venv/bin/activate

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Seed database (optional - comment out if already seeded)
echo "Seeding database..."
python -m src.scripts.seed_data

# Start development server
echo "Starting FastAPI server on http://localhost:8000"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

