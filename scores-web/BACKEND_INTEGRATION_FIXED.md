# Backend Integration Fix - CamelCase Issue Resolved ✅

## Problem
The Next.js frontend was not displaying tournaments from the FastAPI backend because:

1. **Field Naming Mismatch**: Backend was returning `snake_case` field names (Python convention), but frontend expected `camelCase` field names (JavaScript convention)
2. **Schema Field Error**: `TournamentSummary` schema expected `season` field but the database model had `season_id`

## Solution

### 1. Created Base CamelCase Model
Created `/home/kuba/dev/scores-server/src/schemas/base.py` with automatic camelCase conversion:

```python
from pydantic import BaseModel, ConfigDict

def to_camel_case(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

class CamelCaseModel(BaseModel):
    """Base model that converts snake_case field names to camelCase in JSON."""
    
    model_config = ConfigDict(
        alias_generator=to_camel_case,
        populate_by_name=True,  # Allow both snake_case and camelCase when parsing
        from_attributes=True,  # Allow ORM model conversion
    )
```

### 2. Updated All Schemas
Updated all Pydantic schemas to inherit from `CamelCaseModel` instead of `BaseModel`:
- `src/schemas/common.py`
- `src/schemas/season.py`
- `src/schemas/player.py`
- `src/schemas/team.py`
- `src/schemas/venue.py`
- `src/schemas/tournament.py`
- `src/schemas/stage.py`
- `src/schemas/pool.py`
- `src/schemas/match.py`
- `src/schemas/match_event.py`
- `src/schemas/spirit.py`
- `src/schemas/stats.py`

### 3. Fixed Field Mapping Issues
In `tournament.py`, mapped `season_id` to `season` field:

```python
class TournamentSummary(CamelCaseModel):
    season: str = Field(validation_alias="season_id")  # Map season_id to season
    # ... other fields
```

### 4. Fixed Import Errors
Corrected `Field` imports in schemas that were importing from wrong module.

## Before & After

### Before (snake_case)
```json
{
  "id": "sky-this",
  "name": "Sky This",
  "short_name": "Sky",
  "founded_year": null,
  "start_date": "2025-11-11",
  "end_date": "2025-11-12"
}
```

### After (camelCase) ✅
```json
{
  "id": "sky-this",
  "name": "Sky This",
  "shortName": "Sky",
  "foundedYear": null,
  "startDate": "2025-11-11",
  "endDate": "2025-11-12"
}
```

## Testing

### Test Backend Endpoints
```bash
# Test teams endpoint
curl -s "http://localhost:8000/v1/teams/" | python3 -m json.tool | head -30

# Test tournaments endpoint
curl -s "http://localhost:8000/v1/tournaments/" | python3 -m json.tool | head -30

# Test health
curl http://localhost:8000/health
```

### Expected Output
All fields should now be in camelCase:
- ✅ `shortName` instead of `short_name`
- ✅ `startDate` instead of `start_date`
- ✅ `endDate` instead of `end_date`
- ✅ `foundedYear` instead of `founded_year`
- ✅ `updatedAt` instead of `updated_at`

## Running the Full Stack

### Terminal 1 - Backend
```bash
cd /home/kuba/dev/scores-server
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
cd /home/kuba/dev/scores-web
npm run dev
# Will run on port 3001 (or 3000 if available)
```

### Access
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Tournaments Page**: http://localhost:3001/tournaments
- **Teams Page**: http://localhost:3001/teams

## Files Changed

### Backend (`/home/kuba/dev/scores-server`)
- ✅ Created `src/schemas/base.py` (new file)
- ✅ Updated all 12 schema files in `src/schemas/`
- ✅ Fixed `Field` imports in `match_event.py` and `spirit.py`
- ✅ Added `validation_alias` for `season` field in `tournament.py`

### No Frontend Changes Needed
The frontend already expected camelCase, so no changes were required there.

## Verification

### 1. Check Backend Returns CamelCase
```bash
curl http://localhost:8000/v1/tournaments/ | python3 -m json.tool
```

Should see fields like: `startDate`, `endDate`, `updatedAt`

### 2. Check Frontend Displays Data
Visit http://localhost:3001/tournaments and verify tournament listings appear.

### 3. Check Browser Console
Open browser DevTools → Network tab → Check API calls to `http://localhost:8000/v1/...`
- Status should be `200 OK`
- Response should show camelCase fields

## Status: ✅ FIXED

The integration is now complete. The backend automatically converts all snake_case field names to camelCase when serializing responses, matching what the Next.js frontend expects.

