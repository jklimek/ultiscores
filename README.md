# Ultimate Frisbee Scores System

A comprehensive monorepo for managing Ultimate Frisbee tournaments with real-time scoring, statistics, and tournament management.

## 🎯 Project Overview

This monorepo contains three integrated applications:

1. **Scores Web** - Next.js frontend for public tournament browsing and live scoring
2. **Scores Server** - FastAPI backend with REST API, WebSocket support, and statistics engine
3. **Admin App** - Streamlit admin panel for tournament creation and database management

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm (for scores-web)
- **Python** 3.12+ (for scores-server and admin)
- **Git** for version control

### One-Command Startup

Run all three applications simultaneously:

```bash
./start-all.sh
```

This will start:
- **Frontend** at http://localhost:3000 (Next.js)
- **Backend API** at http://localhost:8000 (FastAPI)
- **Admin Panel** at http://localhost:8501 (Streamlit)

To stop all services, press `Ctrl+C`.

### Manual Setup

If you prefer to run each app separately:

#### 1. Setup Scores Server (Backend)

```bash
cd scores-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
alembic upgrade head

# Seed sample data
python -m src.scripts.seed_data

# Run server
uvicorn src.main:app --reload --port 8000
```

#### 2. Setup Scores Web (Frontend)

```bash
cd scores-web

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local

# Edit .env.local:
# NEXT_PUBLIC_USE_API_MOCKS=false
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Run development server
npm run dev
```

#### 3. Setup Admin App

```bash
cd scores-server

# Activate virtual environment (if not already active)
source venv/bin/activate

# Run admin app
streamlit run admin_app.py
```

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

## 📁 Project Structure

```
ultiscores/
├── scores-web/              # Next.js frontend
│   ├── src/
│   │   ├── app/            # Next.js App Router pages
│   │   │   ├── (public)/  # Public pages (tournaments, teams, players)
│   │   │   └── (admin)/   # Admin pages (match control)
│   │   ├── components/     # React components
│   │   └── lib/           # API client, utilities, schemas
│   ├── docs/              # Frontend documentation
│   └── package.json
│
├── scores-server/          # FastAPI backend
│   ├── src/
│   │   ├── main.py        # FastAPI app entry point
│   │   ├── models/        # SQLAlchemy database models
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic (stats, tournaments, scheduler)
│   │   ├── websocket/     # WebSocket handlers
│   │   └── scripts/       # Utility scripts
│   ├── admin_app.py       # Streamlit admin panel
│   ├── alembic/           # Database migrations
│   └── requirements.txt
│
├── docs/                   # Consolidated documentation
│   ├── API_CONTRACTS.md
│   ├── ARCHITECTURE.md
│   └── ADMIN_GUIDE.md
│
├── start-all.sh           # Unified startup script
└── README.md              # This file
```

## 🎮 Features

### Scores Web (Frontend)
- **Public Pages**: Tournament browsing, team profiles, player statistics, live matches
- **Live Scoring Interface**: Real-time match control panel for scorekeepers
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark/Light Themes**: Automatic theme switching with system preference detection
- **Real-time Updates**: WebSocket integration for live score updates

### Scores Server (Backend)
- **REST API**: Complete CRUD operations for tournaments, matches, teams, and players
- **WebSocket Server**: Real-time match event broadcasting at `ws://localhost:8000/ws/matches/{matchId}`
- **Statistics Engine**: Automatic calculation of:
  - Holds and breaks (offensive/defensive efficiency)
  - Possession time percentages
  - Player statistics (goals, assists, blocks, turnovers)
  - Team statistics
- **Tournament Generator**: Support for multiple formats:
  - Pool play with round-robin
  - Swiss system pairing
  - Power pools (championship/consolation)
  - Single/double elimination brackets
- **Smart Scheduler**: Match scheduling with configurable rest periods and field allocation
- **Spirit of the Game**: Track and rank SOTG scores

### Admin App (Streamlit)
- **Database Preview**: Browse all tables with pagination and CSV export
- **Tournament Creation**: Complete tournament setup wizard with:
  - Format selection (pools, Swiss, power pools, playoffs)
  - Team selection and seeding
  - Match scheduling configuration
  - Automatic structure generation
- **Authentication**: Secure login with session management

## 🔧 Technology Stack

### Frontend
- **Next.js 15** with App Router and Server Components
- **TypeScript** for type safety
- **Tailwind CSS 4** for styling
- **shadcn/ui** for UI components
- **Zod** for schema validation
- **Vitest** for testing
- **Storybook** for component documentation

### Backend
- **FastAPI** for REST API
- **SQLAlchemy 2.0** with async support
- **Alembic** for database migrations
- **WebSockets** for real-time communication
- **SQLite** (dev) / **PostgreSQL** (prod)
- **Pytest** for testing

### Admin
- **Streamlit** for rapid UI development
- **Pandas** for data manipulation

## 📚 Documentation

- [API Contracts](docs/API_CONTRACTS.md) - REST and WebSocket API documentation
- [Architecture](docs/ARCHITECTURE.md) - System architecture and design decisions
- [Admin Guide](docs/ADMIN_GUIDE.md) - Admin panel user guide

## 🧪 Development

### Running Tests

**Frontend Tests:**
```bash
cd scores-web
npm run test
npm run lint
```

**Backend Tests:**
```bash
cd scores-server
source venv/bin/activate
pytest
```

### Database Migrations

**Create new migration:**
```bash
cd scores-server
alembic revision --autogenerate -m "description"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback:**
```bash
alembic downgrade -1
```

## 🌐 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Security Notes

**Production Deployment:**
1. Change default admin credentials (use environment variables)
2. Use HTTPS for all services
3. Configure CORS properly for production domains
4. Use PostgreSQL instead of SQLite
5. Set strong SECRET_KEY for FastAPI
6. Enable rate limiting
7. Implement proper authentication for admin endpoints

## 📦 Environment Variables

### Scores Web (.env.local)
```env
NEXT_PUBLIC_USE_API_MOCKS=false
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_LIVE_WS_URL=ws://localhost:8000
```

### Scores Server (.env)
```env
DATABASE_URL=sqlite:///./scores.db
# or for PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost/scores

SECRET_KEY=your-secret-key-here
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]

# Admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

## 🐛 Troubleshooting

### Port Already in Use
If ports 3000, 8000, or 8501 are already in use:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Locked
If SQLite database is locked:
```bash
cd scores-server
rm scores.db
alembic upgrade head
python -m src.scripts.seed_data
```

### Frontend Not Connecting to Backend
1. Ensure backend is running on port 8000
2. Check `.env.local` has correct `NEXT_PUBLIC_API_BASE_URL`
3. Verify CORS is configured in backend
4. Check browser console for errors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - See individual project directories for details.

## 👥 Authors

Built by the Polish Ultimate Frisbee community, for players and organizers.

Inspired by:
- [scores.frisbee.pl](https://scores.frisbee.pl) - Polish Ultimate scoring system
- [live.ebucc.eu](https://live.ebucc.eu) - European tournament live scoring

## 🙏 Acknowledgments

- **Polskie Stowarzyszenie Graczy Ultimate (PSGU)** - Polish Ultimate Players Association
- All contributors and testers from the Polish Ultimate community
- The Ultimate Frisbee community worldwide

---

**Need Help?** Check the documentation in the `docs/` directory or open an issue on GitHub.

