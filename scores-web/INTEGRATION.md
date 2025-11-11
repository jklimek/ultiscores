# Frontend-Backend Integration Guide

## ✅ Integration Complete!

The Next.js frontend is now successfully integrated with the FastAPI backend.

> **🎉 Latest Update**: The field naming issue (snake_case vs camelCase) has been resolved! All backend responses now automatically use camelCase field names, matching what the frontend expects. See [`BACKEND_INTEGRATION_FIXED.md`](./BACKEND_INTEGRATION_FIXED.md) for technical details.

## Changes Made

### 1. Environment Configuration
Created `.env.example` with backend connection settings:
```env
NEXT_PUBLIC_USE_API_MOCKS=false
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_LIVE_WS_URL=ws://localhost:8000
```

### 2. API Client Updates (`src/lib/api/client.ts`)
- ✅ Updated response schema handlers (FastAPI returns data directly, not wrapped)
- ✅ Removed `.data` property access from all API methods
- ✅ Added trailing slashes to list endpoints (FastAPI requirement)
- ✅ Updated all 10 API client methods to work with FastAPI responses

### 3. Response Format Changes
**Before (expected wrapper):**
```json
{
  "data": [...],
  "meta": { "page": 1, ... }
}
```

**After (FastAPI direct response):**
```json
[...]
```

## Running the Full Stack

### Start Backend (Terminal 1)
```bash
cd /home/kuba/dev/scores-server
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

**Backend will be available at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Start Frontend (Terminal 2)
```bash
cd /home/kuba/dev/scores-web
npm run dev
```

**Frontend will be available at:**
- App: http://localhost:3000

## Testing the Integration

### 1. Test Backend Directly
```bash
# List teams
curl http://localhost:8000/v1/teams/ | jq '.[0]'

# Get tournament
curl http://localhost:8000/v1/tournaments/mpx-2025 | jq '.name'

# List matches
curl http://localhost:8000/v1/matches/ | jq 'length'
```

### 2. Test Frontend Pages
Visit these URLs in your browser:
- **Home:** http://localhost:3000
- **Teams:** http://localhost:3000/teams
- **Tournaments:** http://localhost:3000/tournaments
- **Tournament Detail:** http://localhost:3000/tournaments/mpx-2025
- **Players:** http://localhost:3000/players
- **Live Matches:** http://localhost:3000/live

### 3. Verify Real Data is Loading
The frontend should now display:
- ✅ 5 Polish Ultimate teams (Sky This, 4Hands, etc.)
- ✅ 11 real players with names from scores.frisbee.pl
- ✅ Mistrzostwa Polski Mixed 2025 tournament
- ✅ Real match data with proper scheduling

## WebSocket Live Scoring (Future)

The WebSocket endpoint is ready but not yet integrated into the frontend UI:

**Connect to live match:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/matches/match-id');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Match update:', data);
};
```

**Message types received:**
- `connection_ack` - Connected successfully
- `match_snapshot` - Full match state
- `score_update` - Score changed
- `event_created` - New goal/turnover/etc
- `timeout_taken` - Team timeout
- `spirit_updated` - Spirit score submitted

## API Endpoints Available

All endpoints documented at http://localhost:8000/docs

**Key endpoints:**
- `GET /v1/seasons/` - List all seasons
- `GET /v1/tournaments/` - List tournaments (with filters)
- `GET /v1/tournaments/{id}` - Tournament detail
- `GET /v1/matches/` - List matches (with filters)
- `GET /v1/matches/{id}` - Match detail with events
- `GET /v1/teams/` - List teams
- `GET /v1/teams/{id}` - Team detail
- `GET /v1/players/` - List players
- `GET /v1/players/{id}` - Player detail
- `POST /v1/admin/matches/{id}/events` - Create match event
- `POST /v1/admin/spirit` - Submit spirit score

## Troubleshooting

### Backend not responding
```bash
# Check if running
ps aux | grep uvicorn

# Check logs
tail -f /tmp/fastapi.log

# Restart
pkill -f uvicorn
cd /home/kuba/dev/scores-server && ./venv/bin/uvicorn src.main:app --reload --port 8000
```

### Frontend showing mock data
Check `.env.local`:
```bash
cat /home/kuba/dev/scores-web/.env.local
```

Should show:
```env
NEXT_PUBLIC_USE_API_MOCKS=false
```

### CORS errors
Backend is configured to allow localhost:3000. If using different port, update `scores-server/src/config.py`:
```python
cors_origins: List[str] = [
    "http://localhost:3000",
    "http://localhost:YOUR_PORT",
]
```

### 404 errors on API calls
- Make sure URLs have trailing slashes for list endpoints
- Check FastAPI logs for actual errors
- Verify database is seeded: `ls -la /home/kuba/dev/scores-server/scores.db`

## Data Flow

```
User Request → Next.js Page (SSR)
            ↓
    API Client (src/lib/api/client.ts)
            ↓
    HTTP Fetch (src/lib/api/http.ts)
            ↓
    FastAPI Backend (localhost:8000)
            ↓
    SQLAlchemy Models
            ↓
    SQLite Database (scores.db)
            ↓
    Pydantic Schemas
            ↓
    JSON Response
            ↓
    Zod Validation
            ↓
    React Components
            ↓
    User Sees Data
```

## Next Steps

1. **Test all pages** - Verify data loads correctly
2. **Implement admin panel** - Use POST endpoints for match events
3. **Add WebSocket** - Real-time live scoring updates
4. **Tournament generator UI** - Create tournaments via frontend
5. **Player stats** - Display calculated statistics
6. **Spirit scores** - Submit and view SOTG scores

## Success Indicators

✅ Backend health check returns `{"status": "healthy"}`
✅ Frontend loads without errors
✅ Teams page shows 5 Polish teams
✅ Tournament page shows "Mistrzostwa Polski Mixed 2025"
✅ Match data displays with correct scores
✅ No CORS errors in browser console
✅ API calls return in < 500ms
✅ Zod validation passes on all responses

---

**Integration Status:** ✅ Complete
**Date:** November 11, 2025
**Version:** 1.0.0

