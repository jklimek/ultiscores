## Scores Web

Modern Ultimate Frisbee tournament tracker with real-time scoring, tournament browsing, and player databases. Built with Next.js 16, Tailwind CSS 4, shadcn/ui, and a typed FastAPI-facing client.

### Getting Started

```bash
# Start Next.js
npm run dev

# Run ESLint
npm run lint

# Run Vitest unit tests
npm run test

# Launch Storybook
npm run storybook
```

### Project Highlights

- Responsive public surfaces for tournaments, teams, players, and live events (`src/app/(public)`).
- Organizer workspace with a match control panel for logging points, turnovers, and timeouts (`src/app/(admin)`).
- Typed Zod contracts & API client to integrate with the upcoming FastAPI backend (`src/lib/api`).
- Mock dataset (`createMockApiClient`) to develop UI while the backend comes online.
- Storybook (Vite builder) with theming decorators and sample stories for design system primitives.

### Documentation

- `docs/api-contracts.md` — REST + websocket expectations for the FastAPI service.
- `docs/architecture.md` — architecture overview and suggested next steps.

### Environment

Copy `.env.example` to `.env.local` and configure:

```bash
cp .env.example .env.local
```

**Using Real Backend:**
```env
NEXT_PUBLIC_USE_API_MOCKS=false
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_LIVE_WS_URL=ws://localhost:8000
```

**Using Mock Data:**
```env
NEXT_PUBLIC_USE_API_MOCKS=true
```

### Running with FastAPI Backend

1. **Start the backend server:**
```bash
cd /home/kuba/dev/scores-server
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

2. **Start the Next.js frontend:**
```bash
cd /home/kuba/dev/scores-web
npm run dev
```

3. **Visit:** http://localhost:3000

The frontend will now fetch real data from the FastAPI backend!
