# Streamlit Admin App

A comprehensive admin panel for the Scores Server, built with Streamlit.

## Features

### 🔐 Authentication
- Basic authentication with username/password
- Secure session management
- Logout functionality

### 📊 Database Preview
- View all database tables
- Browse table schemas (columns, types, constraints)
- Paginated data viewing
- Export tables to CSV
- Real-time row and column counts

### ➕ Tournament Creation
- Complete tournament creation form with all settings:
  - **Basic Info**: Name, slug, season, division, dates, venue, status
  - **Tournament Settings**: Format, pools, rest periods, match duration, fields
  - **Game Rules**: Point cap, soft cap, hard cap
  - **Power Pools**: Championship pool size configuration
  - **Organiser Info**: Name, website, contact email
  - **Team Selection**: Multi-select with division filtering
  - **Team Seeding**: Assign seeds to each team
- Automatic tournament structure generation
- Match scheduling integration
- Real-time validation and error handling

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the database exists:
```bash
# Run migrations
alembic upgrade head

# Seed sample data (optional)
python -m src.scripts.seed_data
```

## Usage

### Quick Start

Run the admin app using the provided script:

```bash
./run_admin.sh
```

Or manually:

```bash
streamlit run admin_app.py
```

The app will open in your browser at `http://localhost:8501`

### Default Credentials

```
Username: admin
Password: admin123
```

**⚠️ Important:** Change these credentials in production! Update them in:
- `admin_app.py` (lines 28-29)
- `src/routers/admin_streamlit.py` (lines 13-14)

Or better yet, use environment variables:

```python
import os
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
```

## API Integration

The admin app also has a FastAPI endpoint with basic auth:

```bash
# Access the admin endpoint (requires basic auth)
curl -u admin:admin123 http://localhost:8000/admin
```

Response:
```json
{
  "message": "Authenticated successfully",
  "username": "admin",
  "streamlit_url": "http://localhost:8501",
  "note": "Run the Streamlit app with: streamlit run admin_app.py"
}
```

## Database Preview

The database preview feature allows you to:

1. **Select any table** from a dropdown
2. **View table schema** with column details
3. **Browse data** with pagination (10-100 rows per page)
4. **Export data** to CSV format
5. **See metrics** (total rows, total columns)

Supported tables:
- `seasons` - Tournament seasons
- `teams` - Team information
- `players` - Player profiles
- `venues` - Tournament venues
- `tournaments` - Tournament details
- `stages` - Tournament stages
- `pools` - Pool play groups
- `matches` - Match schedule and results
- `match_events` - Event timeline
- `player_stats` - Player statistics
- `team_stats` - Team statistics
- `spirit_scores` - Spirit of the Game scores
- `tournament_rosters` - Team rosters per tournament

## Tournament Creation

### Step-by-Step Guide

1. **Login** with admin credentials

2. **Navigate** to "Create Tournament" in the sidebar

3. **Fill Basic Information**:
   - Tournament name (e.g., "Mistrzostwa Polski Mixed 2025")
   - Unique slug (e.g., "mp-mixed-2025")
   - Select season from existing seasons
   - Choose division (mixed, open, women, junior, masters)
   - Set start and end dates
   - Select venue
   - Set status (upcoming, in_progress, completed, cancelled)

4. **Configure Tournament Settings**:
   - **Format**: Choose from:
     - `power_pools` - Top teams advance to championship pool
     - `pool` - Standard pool play
     - `swiss` - Swiss system pairing
     - `single_elim` - Single elimination bracket
     - `double_elim` - Double elimination bracket
   - **Pool Count**: Number of pools (for pool formats)
   - **Rest Periods**: Minimum matches between games for a team
   - **Match Duration**: Game length in minutes
   - **Field Count**: Number of fields available
   - **Point Cap**: Game ends when team reaches this score
   - **Soft Cap**: Time when soft cap triggers
   - **Hard Cap**: Time when hard cap triggers
   - **Power Pool Size**: Teams advancing to championship pool

5. **Add Organiser Information** (optional):
   - Organiser name
   - Website URL
   - Contact email

6. **Select Teams**:
   - Teams are automatically filtered by division
   - Multi-select participating teams
   - Assign unique seeds to each team (1 = highest)

7. **Create Tournament**:
   - Click "Create Tournament" button
   - System will:
     - Create tournament record
     - Generate stages and pools
     - Create all matches
     - Schedule matches across fields
   - View success message with summary

### Tournament Generation

The app uses the `tournament_generator.py` service to automatically:

- **Distribute teams** to pools using snake seeding
- **Generate matches** based on format:
  - Round-robin for pool play
  - Swiss pairings for Swiss system
  - Bracket pairings for elimination
- **Create stages** (Pool Play, Championship Pool, etc.)
- **Schedule matches** with rest period enforcement

### Example Tournament

```
Name: Mistrzostwa Polski Mixed 2025
Slug: mp-mixed-2025
Division: mixed
Format: power_pools
Teams: 8 teams (Sky This, 4Hands, etc.)
Pools: 2 pools (A and B)
Power Pool: Top 4 teams advance

Generated Structure:
- Stage 1: Pool Play (2 pools, 12 matches)
- Stage 2: Championship Pool (4 teams)
- Stage 3: Consolation Pool (4 teams)
```

## Architecture

### Tech Stack
- **Frontend**: Streamlit 1.39.0
- **Backend**: FastAPI + SQLAlchemy (async)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Data Processing**: Pandas 2.2.0

### File Structure
```
scores-server/
├── admin_app.py              # Main Streamlit app
├── run_admin.sh              # Startup script
├── src/
│   ├── routers/
│   │   └── admin_streamlit.py  # FastAPI /admin endpoint
│   ├── services/
│   │   └── tournament_generator.py  # Tournament logic
│   └── models/               # Database models
└── ADMIN_APP_README.md       # This file
```

### Database Connection

The app uses SQLite for direct database access (for preview) and SQLAlchemy async sessions for tournament creation:

```python
# Direct SQLite (for preview)
conn = sqlite3.connect("scores.db")
df = pd.read_sql_query("SELECT * FROM teams", conn)

# Async SQLAlchemy (for creation)
async with AsyncSessionLocal() as db:
    tournament = Tournament(...)
    db.add(tournament)
    await db.commit()
```

## Security Considerations

### Production Deployment

1. **Change default credentials**:
   ```bash
   export ADMIN_USERNAME="your_secure_username"
   export ADMIN_PASSWORD="your_secure_password"
   ```

2. **Use HTTPS** for the Streamlit app:
   ```bash
   streamlit run admin_app.py \
     --server.sslCertFile=/path/to/cert.pem \
     --server.sslKeyFile=/path/to/key.pem
   ```

3. **Restrict network access**:
   ```bash
   # Only allow localhost
   streamlit run admin_app.py --server.address 127.0.0.1
   
   # Or use a reverse proxy (nginx, caddy)
   ```

4. **Add rate limiting** to prevent brute force attacks

5. **Enable audit logging** for admin actions

6. **Use environment variables** for all secrets

## Troubleshooting

### Database Not Found
```
Error: unable to open database file
```
**Solution**: Run `alembic upgrade head` to create the database

### No Seasons/Teams/Venues
```
Error: No seasons found. Please create a season first.
```
**Solution**: Run `python -m src.scripts.seed_data` to populate sample data

### Import Errors
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution**: Install dependencies with `pip install -r requirements.txt`

### Port Already in Use
```
Error: Port 8501 is already in use
```
**Solution**: Stop other Streamlit instances or use a different port:
```bash
streamlit run admin_app.py --server.port 8502
```

### Authentication Loop
If you're stuck in a login loop, clear Streamlit cache:
```bash
rm -rf ~/.streamlit/cache
```

## Development

### Running in Development Mode

```bash
# Terminal 1: Run FastAPI server
uvicorn src.main:app --reload --port 8000

# Terminal 2: Run Streamlit admin
streamlit run admin_app.py --server.port 8501
```

### Adding New Features

1. **Add a new page**: Create a new function in `admin_app.py`
2. **Add to navigation**: Update the sidebar radio options
3. **Test thoroughly**: Ensure database operations are atomic

### Debugging

Enable debug mode in Streamlit:
```bash
streamlit run admin_app.py --logger.level=debug
```

View SQL queries:
```python
# In src/config.py
debug: bool = True  # Enables SQLAlchemy echo
```

## Future Enhancements

- [ ] Match scheduling visualization (Gantt chart)
- [ ] Team/player management (CRUD operations)
- [ ] Live match scoring interface
- [ ] Tournament standings calculator
- [ ] Spirit score submission form
- [ ] Statistics dashboard
- [ ] Export tournament to PDF
- [ ] Import teams from CSV
- [ ] Multi-user support with roles
- [ ] Audit log viewer

## Support

For issues or questions:
1. Check the main [README.md](README.md)
2. Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
3. Check FastAPI docs at `http://localhost:8000/docs`

## License

MIT License - Same as the main Scores Server project

