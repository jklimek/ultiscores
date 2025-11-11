# Admin App User Guide

A comprehensive guide for using the Streamlit admin panel to manage tournaments and database operations.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Database Preview](#database-preview)
4. [Tournament Creation](#tournament-creation)
5. [Troubleshooting](#troubleshooting)

## Getting Started

### Accessing the Admin Panel

1. **Start the admin app**:
   ```bash
   cd scores-server
   ./run_admin.sh
   ```
   Or manually:
   ```bash
   streamlit run admin_app.py
   ```

2. **Open in browser**: http://localhost:8501

3. **Login** with default credentials:
   - Username: `admin`
   - Password: `admin123`

### Navigation

The sidebar provides access to main features:
- **Database Preview** - Browse and export data
- **Create Tournament** - Tournament creation wizard
- **Logout** - End your session

## Authentication

### Login Process

1. Enter your username and password
2. Click "Login"
3. Session persists until logout or browser close

### Security Notes

⚠️ **Important**: Default credentials should be changed in production!

**To change credentials**, edit these files:
- `admin_app.py` (lines 28-29)
- `src/routers/admin_streamlit.py` (lines 13-14)

**Better approach** - Use environment variables:
```bash
export ADMIN_USERNAME="your_username"
export ADMIN_PASSWORD="your_secure_password"
```

## Database Preview

Browse and analyze database tables directly from the admin panel.

### Features

#### 1. Table Selection

- **Dropdown menu** lists all available tables
- **Real-time metrics** show row and column counts
- Tables automatically refresh when selected

#### 2. Schema Viewing

For each table, view:
- **Column name**: Database field name
- **Data type**: SQL data type
- **Nullable**: Whether NULL values are allowed
- **Primary key**: Identifies primary key columns

#### 3. Data Browsing

- **Pagination**: Control rows per page (10, 25, 50, 100)
- **Page navigation**: Jump to any page
- **Data display**: Formatted table with all columns
- **Empty states**: Clear messaging when no data exists

#### 4. Data Export

- **CSV export**: Download table data
- **Filename**: Auto-generated as `{table_name}.csv`
- **Full data**: Exports all rows, not just current page

### Available Tables

| Table | Description |
|-------|-------------|
| `seasons` | Tournament seasons (year, name) |
| `teams` | Team information (name, city, division) |
| `players` | Player profiles (name, jersey number) |
| `venues` | Tournament venues (name, address, fields) |
| `tournaments` | Tournament details (name, dates, settings) |
| `stages` | Tournament stages (pool play, playoffs) |
| `pools` | Pool groups within stages |
| `matches` | Match schedule and results |
| `match_events` | Event timeline (goals, turnovers) |
| `player_stats` | Player statistics per match |
| `team_stats` | Team statistics per match |
| `spirit_scores` | Spirit of the Game scores |
| `tournament_rosters` | Team rosters per tournament |

### Example Use Cases

**Find all mixed teams:**
1. Select `teams` table
2. Look at "division" column
3. Filter for "mixed" values

**Export tournament schedule:**
1. Select `matches` table
2. Find your tournament_id
3. Click "Export to CSV"

**Check player statistics:**
1. Select `player_stats` table
2. Browse by match_id or player_id
3. View goals, assists, blocks, etc.

## Tournament Creation

Step-by-step guide to creating a complete tournament with automatic structure generation.

### Prerequisites

Before creating a tournament, ensure you have:
- ✅ At least one **season** in the database
- ✅ At least one **venue** defined
- ✅ Teams matching your tournament **division**

Run seed data if needed:
```bash
python -m src.scripts.seed_data
```

### Step 1: Basic Information

**Tournament Name**
- Full tournament name (e.g., "Mistrzostwa Polski Mixed 2025")
- Displayed on all public pages

**URL Slug**
- Unique identifier for URLs
- Use lowercase, hyphens for spaces
- Example: "mp-mixed-2025"

**Season**
- Select from existing seasons
- Creates season grouping

**Division**
- Choose: `mixed`, `open`, `women`, `junior`, or `masters`
- Filters available teams

**Dates**
- **Start date**: First day of tournament
- **End date**: Last day of tournament
- Used for scheduling

**Venue**
- Select from existing venues
- Determines available fields

**Status**
- `upcoming` - Not yet started
- `in_progress` - Currently running
- `completed` - Finished
- `cancelled` - Cancelled

### Step 2: Tournament Settings

**Format**
Choose tournament structure:

| Format | Description | Best For |
|--------|-------------|----------|
| `power_pools` | Top teams → championship pool<br>Others → consolation | Large tournaments (8-16 teams) |
| `pool` | Standard pool play + playoffs | Medium tournaments (6-12 teams) |
| `swiss` | Pair teams with similar records | Flexible schedules |
| `single_elim` | Single elimination bracket | Time-constrained |
| `double_elim` | Double elimination bracket | Fair for small fields |

**Pool Count**
- Number of initial pools (typically 2-4)
- Teams distributed by snake seeding
- Only for pool-based formats

**Rest Periods**
- Minimum matches a team sits out between games
- Default: 1 (one match break)
- Higher values = more recovery time

**Match Duration**
- Length of each game in minutes
- Default: 60 minutes
- Used for schedule calculations

**Field Count**
- Number of fields available
- Determines simultaneous matches
- Must match venue configuration

### Step 3: Game Rules

**Point Cap**
- Score to win the game
- Standard: 15 or 17 points
- Game ends when reached

**Soft Cap**
- Time when soft cap triggers
- Example: 75 minutes
- Next team to score wins (if >= cap-2)

**Hard Cap**
- Absolute time limit
- Example: 90 minutes
- Higher score wins, or +1 if tied

### Step 4: Power Pools (if applicable)

Only shown if format is `power_pools`.

**Championship Pool Size**
- Number of top teams advancing
- Example: 4 (top 2 from each pool)
- Creates championship bracket

**Consolation Pool Size**
- Remaining teams
- Calculated automatically
- Creates consolation bracket

### Step 5: Organiser Information (Optional)

**Organiser Name**
- Organization running the tournament
- Example: "Polskie Stowarzyszenie Graczy Ultimate"

**Website URL**
- Tournament or organization website
- Example: "https://psgu.pl"

**Contact Email**
- Email for inquiries
- Example: "info@psgu.pl"

### Step 6: Team Selection

**Team Selection**
- Multi-select from available teams
- **Filtered by division** automatically
- Must select at least 2 teams

**Team Seeding**
- Assign seed number to each selected team
- **1 = highest seed** (strongest team)
- Seeds must be unique
- Used for pool distribution and brackets

**Seeding Strategy:**
- Top seed (1) should be strongest team
- Seeds determine pool placement:
  - Pool A: 1, 4, 5, 8, 9, 12...
  - Pool B: 2, 3, 6, 7, 10, 11...

### Step 7: Review and Create

**Before Creating:**
- Review all settings in the expander
- Check team count and seeds
- Verify dates and venue

**Click "Create Tournament"**

**What Happens:**
1. ✅ Tournament record created
2. ✅ Stages generated (Pool Play, Playoffs)
3. ✅ Pools created with teams
4. ✅ Matches generated (round-robin, brackets)
5. ✅ Matches scheduled across fields
6. ✅ Success message with summary

### Example Tournament

```
Tournament: Mistrzostwa Polski Mixed 2025
Format: power_pools
Teams: 8 teams
Pools: 2 pools (A and B)

Pool A:
- Sky This (seed 1)
- Wrocław Panthers (seed 4)
- Team E (seed 5)
- Team H (seed 8)

Pool B:
- 4Hands (seed 2)
- Poznań Hussars (seed 3)
- Team F (seed 6)
- Team G (seed 7)

Generated Structure:
- Stage 1: Pool Play
  - Pool A: 6 matches (round-robin)
  - Pool B: 6 matches (round-robin)
- Stage 2: Championship Pool
  - Top 2 from each pool
  - 6 matches (round-robin)
- Stage 3: Consolation Pool
  - Bottom 2 from each pool
  - 6 matches (round-robin)

Total: 18 matches scheduled across available fields
```

## Troubleshooting

### Common Issues

#### 1. Database Not Found

**Error**: `unable to open database file`

**Solution**:
```bash
cd scores-server
alembic upgrade head
```

#### 2. No Seasons/Teams/Venues

**Error**: `No seasons found. Please create a season first.`

**Solution**:
```bash
python -m src.scripts.seed_data
```

#### 3. Port Already in Use

**Error**: `Port 8501 is already in use`

**Solution**:
```bash
# Find process
lsof -i :8501

# Kill process
kill -9 <PID>

# Or use different port
streamlit run admin_app.py --server.port 8502
```

#### 4. Authentication Loop

**Problem**: Stuck in login loop

**Solution**:
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/cache

# Restart browser
```

#### 5. Import Errors

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
cd scores-server
source venv/bin/activate
pip install -r requirements.txt
```

#### 6. Tournament Creation Fails

**Error**: `Failed to create tournament`

**Possible Causes**:
- Duplicate slug (must be unique)
- No teams in selected division
- Invalid seed numbers (duplicates or missing)
- Database constraint violation

**Debug Steps**:
1. Check error message details
2. Verify database has required data
3. Ensure slug is unique
4. Confirm all seeds are unique integers

### Getting Help

1. **Check logs**: Streamlit console output shows detailed errors
2. **Database preview**: Use to verify data exists
3. **API docs**: http://localhost:8000/docs shows backend status
4. **Main README**: See project root README.md

### Debug Mode

**Enable verbose logging:**
```bash
streamlit run admin_app.py --logger.level=debug
```

**Check SQL queries:**
```python
# In src/config.py
debug: bool = True  # Enables SQLAlchemy echo
```

## Best Practices

### Tournament Planning

1. **Create season first**: Organize tournaments by year
2. **Add venues**: Define fields before tournaments
3. **Register teams**: Ensure all teams exist in database
4. **Seed properly**: Accurate seeding improves bracket quality
5. **Test schedules**: Check field allocation and rest periods

### Database Management

1. **Regular backups**: Export important tables to CSV
2. **Check integrity**: Browse tables after major operations
3. **Clean old data**: Archive completed tournaments
4. **Monitor size**: SQLite performance degrades with large datasets

### Security

1. **Change credentials**: Update default admin password
2. **Restrict access**: Use firewall rules for admin port
3. **Use HTTPS**: Enable SSL in production
4. **Audit logs**: Track admin actions
5. **Regular updates**: Keep dependencies current

## Advanced Features

### API Integration

The admin app can be accessed via FastAPI endpoint:

```bash
# Test authentication
curl -u admin:admin123 http://localhost:8000/admin
```

**Response:**
```json
{
  "message": "Authenticated successfully",
  "username": "admin",
  "streamlit_url": "http://localhost:8501"
}
```

### Database Direct Access

For advanced users, direct SQLite access:

```bash
sqlite3 scores.db

# List tables
.tables

# Query data
SELECT * FROM tournaments LIMIT 5;

# Exit
.quit
```

### Bulk Operations

**Import teams from CSV:**
```python
# In Python shell
import pandas as pd
from src.database import AsyncSessionLocal
from src.models.team import Team

df = pd.read_csv('teams.csv')
async with AsyncSessionLocal() as db:
    for _, row in df.iterrows():
        team = Team(
            name=row['name'],
            city=row['city'],
            division=row['division']
        )
        db.add(team)
    await db.commit()
```

## Keyboard Shortcuts

Streamlit keyboard shortcuts:

- **R** - Rerun the app
- **C** - Clear cache
- **Ctrl + Shift + R** - Hard reload
- **Esc** - Close modal dialogs

## FAQ

**Q: Can I edit existing tournaments?**
A: Not yet. This feature is planned for future releases.

**Q: How do I delete a tournament?**
A: Use database preview to note the ID, then use SQL or Python script.

**Q: Can I create custom tournament formats?**
A: Not through the UI. You can modify `tournament_generator.py` for custom logic.

**Q: Does the admin app support multiple users?**
A: Currently single-user with shared credentials. Multi-user support is planned.

**Q: Can I run admin app remotely?**
A: Yes, but use HTTPS and strong authentication in production.

---

**Need more help?** See the main [README.md](../README.md) or [ARCHITECTURE.md](ARCHITECTURE.md) for technical details.

