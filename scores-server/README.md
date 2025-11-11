# Scores Server

FastAPI backend for Ultimate Frisbee tournament management with real-time scoring, statistics calculation, and tournament generation.

## Features

- **Tournament Management**: Create tournaments with flexible formats (pools, Swiss, power pools, playoffs)
- **Live Scoring**: WebSocket-based real-time match event broadcasting
- **Statistics Engine**: Automatic calculation of holds, breaks, possession time, player stats
- **Smart Scheduling**: Match scheduler with configurable rest periods and field allocation
- **Spirit of the Game**: Track and rank SOTG scores

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Initialize database
alembic upgrade head

# Seed sample data
python -m src.scripts.seed_data

# Run development server
uvicorn src.main:app --reload --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## WebSocket

Connect to live match updates:
```
ws://localhost:8000/ws/matches/{matchId}
```

## Project Structure

```
src/
├── main.py              # FastAPI app
├── config.py            # Settings
├── database.py          # Database connection
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── routers/             # API endpoints
├── services/            # Business logic
│   ├── stats.py         # Statistics engine
│   ├── tournament_generator.py
│   └── scheduler.py
├── websocket/           # WebSocket handlers
└── utils/               # Utilities
```

## Development

```bash
# Run tests
pytest

# Generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1
```

## Tournament Formats

- **Pool Play**: Round-robin within pools, configurable advancement
- **Swiss System**: Pair teams with similar records, no repeat matchups
- **Power Pools**: Top teams advance to championship pool, others to consolation
- **Cross Matches**: Direct placement matches between pool positions (A2 vs B2)
- **Playoffs**: Single/double elimination brackets

## License

MIT

