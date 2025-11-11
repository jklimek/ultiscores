# Scores System Architecture

## Overview

The Ultimate Frisbee Scores System is a full-stack monorepo application with three main components working together to provide real-time tournament management and scoring.

## System Components

### 1. Scores Web (Frontend)

**Technology**: Next.js 15 with App Router, TypeScript, Tailwind CSS 4, shadcn/ui

**Purpose**: Public-facing website and admin control panel for live scoring

**Key Features**:
- Server Components for optimal data fetching
- Real-time WebSocket integration for live updates
- Responsive design with dark/light theme support
- Typed API client with Zod schema validation

**Directory Structure**:
```
src/
  app/                    # Next.js routes
    (public)/             # Public surfaces (tournaments, teams, players, live hub)
    (admin)/              # Organizer workspace (match control panel)
    layout.tsx            # Global ThemeProvider + AppShell navigation
  components/
    admin/                # Live scoring control UI
    layout/               # App-wide shell, toggles, navigation
    ui/                   # Reusable design system elements (shadcn + custom timeline)
  lib/
    api/                  # Zod schemas, API client, realtime message contracts, mock data
    env.ts                # Runtime environment helpers
    format.ts             # Date/division formatting helpers
    utils.ts              # Tailwind class merge helpers
```

### 2. Scores Server (Backend)

**Technology**: FastAPI, SQLAlchemy 2.0 (async), Alembic, WebSockets

**Purpose**: REST API, WebSocket server, and business logic engine

**Key Features**:
- RESTful API with automatic OpenAPI documentation
- WebSocket server for real-time match event broadcasting
- Statistics calculation engine
- Tournament generation with multiple format support
- Smart match scheduler with rest period enforcement

**Directory Structure**:
```
src/
├── main.py              # FastAPI app initialization
├── config.py            # Settings and configuration
├── database.py          # Database connection and session management
├── models/              # SQLAlchemy ORM models
│   ├── season.py
│   ├── team.py
│   ├── player.py
│   ├── tournament.py
│   ├── match.py
│   └── ...
├── schemas/             # Pydantic schemas for validation
├── routers/             # API endpoint routers
│   ├── seasons.py
│   ├── tournaments.py
│   ├── matches.py
│   ├── teams.py
│   ├── players.py
│   └── admin.py
├── services/            # Business logic services
│   ├── stats.py         # Statistics calculation engine
│   ├── tournament_generator.py  # Tournament structure generation
│   └── scheduler.py     # Match scheduling logic
├── websocket/           # WebSocket connection management
│   └── manager.py
├── utils/               # Utility functions
└── scripts/             # Maintenance scripts
    └── seed_data.py
```

### 3. Admin App

**Technology**: Streamlit, Pandas

**Purpose**: Administrative interface for tournament creation and database management

**Key Features**:
- Database browser with table preview and CSV export
- Tournament creation wizard with comprehensive settings
- Secure authentication with session management
- Direct integration with backend services

## Data Flow Architecture

### Request Flow (REST API)

```
┌─────────────┐        HTTP Request         ┌──────────────┐
│             │──────────────────────────────>│              │
│  Scores Web │                               │ Scores Server│
│  (Next.js)  │<──────────────────────────────│  (FastAPI)   │
│             │        JSON Response          │              │
└─────────────┘                               └──────┬───────┘
                                                     │
                                                     │ SQL
                                                     │
                                              ┌──────▼───────┐
                                              │   Database   │
                                              │   (SQLite/   │
                                              │  PostgreSQL) │
                                              └──────────────┘
```

### Real-time Flow (WebSocket)

```
┌─────────────┐      WS: connect             ┌──────────────┐
│             │─────────────────────────────>│              │
│  Scores Web │                              │ Scores Server│
│  (Client)   │                              │  (WebSocket) │
│             │<────────────────────────────│              │
└─────────────┘   WS: match updates          └──────────────┘
                  (events, scores, etc.)
```

### Admin Flow

```
┌─────────────┐     Create Tournament       ┌──────────────┐
│             │─────────────────────────────>│              │
│  Admin App  │                              │ Tournament   │
│ (Streamlit) │                              │  Generator   │
│             │<────────────────────────────│              │
└─────────────┘      Confirmation            └──────┬───────┘
                                                     │
                                                     │ Insert
                                                     │
                                              ┌──────▼───────┐
                                              │   Database   │
                                              └──────────────┘
```

## Database Schema

### Core Entities

```
Season
  ├── id, year, name
  └── tournaments[]

Team
  ├── id, name, city, division
  └── players[] (via tournament_rosters)

Player
  ├── id, name, jersey_number
  └── stats[]

Tournament
  ├── id, name, slug, season_id
  ├── division, status, dates
  ├── settings (JSON: format, pools, caps, etc.)
  └── stages[]

Stage
  ├── id, tournament_id, name, type
  └── pools[]

Pool
  ├── id, stage_id, name
  ├── teams (JSON array)
  └── matches[]

Match
  ├── id, tournament_id, pool_id
  ├── home_team_id, away_team_id
  ├── home_score, away_score
  ├── status, scheduled_at, field_id
  └── events[]

MatchEvent
  ├── id, match_id, sequence, timestamp
  ├── type (goal, turnover, timeout, etc.)
  └── data (JSON: player_ids, event-specific fields)

PlayerStats
  └── goals, assists, blocks, turnovers, points_played

TeamStats
  └── holds, breaks, possession_pct, offensive_efficiency

SpiritScore
  └── 5 category scores, total, notes
```

## API Client Layer

The frontend uses a typed API client that:

1. **Validates requests/responses** using Zod schemas
2. **Handles errors** gracefully with fallback to mocks
3. **Supports both environments**:
   - Mock data for local development (`NEXT_PUBLIC_USE_API_MOCKS=true`)
   - Real API for production (`NEXT_PUBLIC_USE_API_MOCKS=false`)
4. **Provides type safety** end-to-end with TypeScript

```typescript
// Example usage
import { getApiClient } from '@/lib/api/server'

const api = getApiClient()
const tournaments = await api.listTournaments({
  division: 'mixed',
  status: 'in_progress'
})
```

## Services Architecture

### Statistics Engine

Processes match event timelines to calculate:
- **Holds**: Points won on offense
- **Breaks**: Points won on defense
- **Possession time**: Percentage of point duration
- **Player stats**: Goals, assists, blocks, turnovers
- **Team efficiency**: Offensive/defensive performance

### Tournament Generator

Creates tournament structures:
- **Pool distribution**: Snake seeding (1,4,5,8 in Pool A; 2,3,6,7 in Pool B)
- **Match generation**: Round-robin, Swiss pairings, brackets
- **Stage creation**: Pool play, championship/consolation pools, playoffs

### Match Scheduler

Optimizes match scheduling:
- **Rest period enforcement**: Minimum matches between games
- **Field allocation**: Balance across available fields
- **Time slot calculation**: Based on duration and turnaround
- **Round grouping**: Simultaneous play optimization

## WebSocket Protocol

### Connection

```
Client -> Server: ws://localhost:8000/ws/matches/{matchId}
Server -> Client: {"type": "connection_ack", "heartbeatInterval": 30000}
```

### Message Types

1. **connection_ack**: Initial handshake confirmation
2. **match_snapshot**: Full match state on connect
3. **score_update**: Score changes
4. **event_created**: New match events (goals, turnovers, etc.)
5. **timeout_taken**: Team timeout notifications
6. **spirit_updated**: Spirit score submissions
7. **error**: Error notifications

### Heartbeat

Clients send heartbeat every 30 seconds to maintain connection:
```json
{"type": "heartbeat", "timestamp": 1234567890}
```

## Security Considerations

### Development
- Default admin credentials (admin/admin123)
- SQLite database (file-based)
- CORS enabled for localhost:3000
- No authentication on public endpoints

### Production Requirements
1. **Authentication**: Implement JWT or session-based auth
2. **HTTPS**: Use TLS certificates for all services
3. **Database**: Migrate to PostgreSQL with connection pooling
4. **CORS**: Restrict to production domains only
5. **Secrets**: Use environment variables for all credentials
6. **Rate Limiting**: Protect API endpoints from abuse
7. **Input Validation**: Sanitize all user inputs
8. **SQL Injection**: Use parameterized queries (SQLAlchemy provides this)

## Performance Optimization

### Frontend
- Server Components for initial data fetching
- Client Components only for interactive features
- Image optimization with Next.js Image component
- Code splitting via dynamic imports

### Backend
- Async SQLAlchemy for concurrent database operations
- Connection pooling for database efficiency
- WebSocket connection management with cleanup
- Pagination for large result sets

### Database
- Indexes on frequently queried columns (team_id, tournament_id, status)
- JSON fields for flexible nested data
- Cascading deletes for referential integrity

## Testing Strategy

### Frontend
- **Vitest**: Unit tests for utilities and helpers
- **Testing Library**: Component integration tests
- **Storybook**: Visual regression testing

### Backend
- **Pytest**: Unit and integration tests
- **In-memory SQLite**: Fast test database
- **Fixtures**: Reusable test data setup

## Deployment Architecture

### Development
```
Local Machine
├── npm run dev (port 3000)
├── uvicorn --reload (port 8000)
└── streamlit run (port 8501)
```

### Production (Recommended)
```
┌─────────────────────────────────────┐
│         Load Balancer / CDN         │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐         ┌──────▼──────┐
│ Vercel │         │   Backend   │
│ (Next) │         │   Server    │
└────────┘         │  (FastAPI)  │
                   │ + WebSocket │
                   └──────┬──────┘
                          │
                   ┌──────▼──────┐
                   │ PostgreSQL  │
                   │  Database   │
                   └─────────────┘

Admin App (Streamlit): Internal network only
```

### Environment Variables

**Frontend (Vercel)**:
```
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomai.com
NEXT_PUBLIC_LIVE_WS_URL=wss://api.yourdomain.com
NEXT_PUBLIC_USE_API_MOCKS=false
```

**Backend (Docker/VPS)**:
```
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/scores
SECRET_KEY=your-secret-key
DEBUG=false
CORS_ORIGINS=["https://yourdomain.com"]
```

## Future Enhancements

### Short-term
- [ ] User authentication with Auth.js
- [ ] Real-time WebSocket integration in frontend
- [ ] Advanced statistics visualizations
- [ ] Mobile app (React Native)

### Medium-term
- [ ] Video integration for live streaming
- [ ] Player tracking with computer vision
- [ ] Advanced tournament formats (bracket reseeding)
- [ ] SMS/email notifications

### Long-term
- [ ] AI-powered game analysis
- [ ] Multi-sport support
- [ ] League management system
- [ ] Officiating assignment tools

## Development Guidelines

### Code Style
- **TypeScript**: Strict mode enabled
- **Python**: Black formatter, isort for imports
- **Linting**: ESLint for TS, Ruff for Python
- **Commits**: Conventional commits format

### Git Workflow
1. Feature branches from `main`
2. Pull requests with review required
3. Automated tests must pass
4. Squash merge to `main`

### Documentation
- Update README for new features
- Add JSDoc/docstrings for public APIs
- Update OpenAPI specs for backend changes
- Keep architecture docs in sync

## Monitoring and Logging

### Frontend
- Next.js built-in logging
- Error boundaries for error handling
- Console warnings in development only

### Backend
- FastAPI automatic request logging
- Custom logger for business logic
- Sentry for error tracking (production)

### Database
- Query logging in development
- Slow query monitoring in production
- Regular backups

## Contact and Support

For questions or contributions:
- Check the main README.md
- Review API documentation at /docs
- Open GitHub issues for bugs
- Discussion forum for feature requests

---

*Last updated: November 2025*

