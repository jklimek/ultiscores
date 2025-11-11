# Testing Guide for Data Model Fixes

## Quick Test Commands

### 1. Check Backend Auto-Reload
```bash
# Backend should auto-reload when files change
# Check the logs:
tail -f /home/kuba/dev/ultiscores/logs/backend.log

# Look for:
# - "Application startup complete"
# - No "ERROR" or "Exception" messages
```

### 2. Test Tournaments Endpoint
```bash
# Should return full Tournament objects with venue, stages, teams
curl -s http://localhost:8000/v1/tournaments/ | python3 -m json.tool | head -150

# Verify response includes:
# - "venue": { "name": "...", "city": "..." }
# - "stages": [...]
# - "teams": [{"teamId": "...", "seed": 1}]
```

### 3. Test Teams Endpoint
```bash
# Should return teams with populated seasons and roster
curl -s http://localhost:8000/v1/teams/ | python3 -m json.tool | head -200

# Verify response includes:
# - "seasons": [{"season": "2025", "division": "mixed", "tournaments": [...]}]
# - "roster": [{"tournamentId": "...", "player": {...}, "jerseyNumber": 10}]
```

### 4. Test Single Team
```bash
# Get specific team with full data
curl -s http://localhost:8000/v1/teams/sky-this | python3 -m json.tool

# Should show:
# - Full roster with player names
# - Season history with tournaments
```

### 5. Check Frontend
```bash
# Watch frontend logs for parsing errors
tail -f /home/kuba/dev/ultiscores/logs/frontend.log | grep -i "failed\|error"

# Should NOT see:
# - "Failed to parse API response"
# - Zod validation errors
```

### 6. Browser Testing
```bash
# Open in browser and check console
echo "Visit: http://localhost:3000/teams"
echo "Visit: http://localhost:3000/tournaments"

# Check browser console (F12) for:
# - No red errors
# - Successful API calls
# - Data rendering properly
```

## Expected Results

### Tournaments List Response
```json
[
  {
    "id": "mpx-2025",
    "slug": "mistrzostwa-polski-mixed-2025",
    "name": "Mistrzostwa Polski Mixed 2025",
    "season": "2025",
    "division": "mixed",
    "startDate": "2025-09-13",
    "endDate": "2025-09-14",
    "status": "upcoming",
    "organiser": {
      "name": "PSGU",
      "website": "https://frisbee.pl"
    },
    "venue": {
      "id": "venue-1",
      "name": "Orlik Bemowo",
      "city": "Warsaw",
      "address": "ul. Powstańców Śląskich 104",
      "fields": [...]
    },
    "stages": [
      {
        "id": "stage-1",
        "name": "Pool Play",
        "stageType": "pool",
        "pools": [...]
      }
    ],
    "teams": [
      {"teamId": "sky-this", "seed": 1},
      {"teamId": "4hands", "seed": 2}
    ],
    "updatedAt": "2025-11-11T01:13:26"
  }
]
```

### Teams List Response
```json
[
  {
    "id": "sky-this",
    "name": "Sky This",
    "shortName": "Sky",
    "slug": "sky-this",
    "division": "mixed",
    "city": "Warsaw",
    "country": "Poland",
    "primaryColor": "#0066CC",
    "secondaryColor": "#FFFFFF",
    "seasons": [
      {
        "season": "2025",
        "division": "mixed",
        "tournaments": [
          {
            "tournamentId": "mpx-2025",
            "tournamentName": "Mistrzostwa Polski Mixed 2025",
            "placement": null,
            "wins": 0,
            "losses": 0
          }
        ]
      }
    ],
    "roster": [
      {
        "tournamentId": "mpx-2025",
        "player": {
          "id": "player-1",
          "name": {
            "first": "Jan",
            "last": "Kowalski",
            "display": "Jan Kowalski"
          },
          "jerseyNumber": 10,
          "pronouns": "he/him",
          "nationality": "Poland",
          "roles": ["handler", "cutter"],
          "stats": null
        },
        "jerseyNumber": 10,
        "captain": true
      }
    ]
  }
]
```

## Troubleshooting

### Backend Not Reloading
```bash
# Manually restart
cd /home/kuba/dev/ultiscores
./stop-all.sh
./start-all-simple.sh
```

### Still Getting Parse Errors
```bash
# Check which field is failing
tail -100 /home/kuba/dev/ultiscores/logs/frontend.log | grep -B 5 "Failed to parse"

# The error will show which Zod validation failed
```

### Empty Arrays Still Showing
```bash
# Check if tournament_rosters table has data
cd /home/kuba/dev/ultiscores/scores-server
sqlite3 scores.db "SELECT COUNT(*) FROM tournament_rosters;"

# Should return > 0
# If 0, need to seed data:
source venv/bin/activate
python3 -m src.scripts.seed_data
```

### Server Errors (500)
```bash
# Check detailed backend logs
tail -100 /home/kuba/dev/ultiscores/logs/backend.log

# Look for Python tracebacks and exceptions
```

## Success Criteria

✅ **All tests pass when:**

1. Backend logs show "Application startup complete"
2. `/v1/tournaments/` returns arrays with venue and stages
3. `/v1/teams/` returns arrays with non-empty seasons and roster
4. Frontend logs show NO "Failed to parse" errors
5. Browser console shows NO red errors
6. Pages render data correctly:
   - Tournaments page shows list with venue info
   - Teams page shows list with season history
   - Individual team pages show roster

## Quick Health Check Script

```bash
#!/bin/bash
echo "=== Backend Health Check ==="
curl -s http://localhost:8000/docs > /dev/null && echo "✓ Backend API running" || echo "✗ Backend down"

echo -e "\n=== Frontend Health Check ==="
curl -s http://localhost:3000 > /dev/null && echo "✓ Frontend running" || echo "✗ Frontend down"

echo -e "\n=== Tournament Endpoint Check ==="
TOURNAMENT_DATA=$(curl -s http://localhost:8000/v1/tournaments/)
echo "$TOURNAMENT_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print('✓ Has venue' if d and 'venue' in d[0] else '✗ Missing venue')"
echo "$TOURNAMENT_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print('✓ Has stages' if d and len(d[0].get('stages', [])) > 0 else '✗ Missing stages')"

echo -e "\n=== Teams Endpoint Check ==="
TEAM_DATA=$(curl -s http://localhost:8000/v1/teams/)
echo "$TEAM_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print('✓ Has seasons' if d and len(d[0].get('seasons', [])) > 0 else '✗ Empty seasons')"
echo "$TEAM_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print('✓ Has roster' if d and len(d[0].get('roster', [])) > 0 else '✗ Empty roster')"

echo -e "\n=== Frontend Errors Check ==="
grep -c "Failed to parse" /home/kuba/dev/ultiscores/logs/frontend.log | python3 -c "import sys; c=int(sys.stdin.read()); print('✗ Parse errors found:', c) if c > 0 else print('✓ No parse errors')"
```

Save as `test-health.sh`, make executable, and run:
```bash
chmod +x test-health.sh
./test-health.sh
```

---

**Created**: 2025-11-11
**Purpose**: Verify data model synchronization fixes between frontend and backend

