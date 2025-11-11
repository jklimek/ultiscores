# Admin App - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### 1. Install Dependencies

```bash
cd /home/kuba/dev/scores-server
source venv/bin/activate  # if using virtual environment
pip install -r requirements.txt
```

### 2. Ensure Database Exists

```bash
# Run migrations
alembic upgrade head

# Seed sample data (optional but recommended)
python -m src.scripts.seed_data
```

### 3. Start the Admin App

```bash
./run_admin.sh
```

Or manually:
```bash
streamlit run admin_app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## 🔐 Login Credentials

```
Username: admin
Password: admin123
```

## 📋 What You Can Do

### Database Preview
- View all 13 database tables
- Browse table schemas and data
- Export tables to CSV
- Paginate through large datasets

### Create Tournament
1. Fill in basic info (name, dates, venue)
2. Configure tournament settings (format, pools, fields)
3. Select and seed teams
4. Click "Create Tournament"
5. System generates all matches automatically!

## 🎯 Example: Create a Tournament

1. **Login** with admin/admin123
2. **Click** "Create Tournament" in sidebar
3. **Fill in**:
   - Name: "Test Tournament 2025"
   - Slug: "test-2025"
   - Season: Select from dropdown
   - Division: "mixed"
   - Dates: Today to tomorrow
   - Venue: Select from dropdown
4. **Configure**:
   - Format: "power_pools"
   - Pool Count: 2
   - Match Duration: 75 minutes
   - Field Count: 2
5. **Select Teams**: Choose 4-8 teams
6. **Assign Seeds**: 1, 2, 3, 4, etc.
7. **Click** "Create Tournament"
8. **Success!** View the generated structure

## 🔧 Troubleshooting

### "No seasons found"
Run: `python -m src.scripts.seed_data`

### "Port 8501 already in use"
Stop other Streamlit apps or use: `streamlit run admin_app.py --server.port 8502`

### "Module not found"
Run: `pip install -r requirements.txt`

## 📚 More Info

- Full documentation: [ADMIN_APP_README.md](ADMIN_APP_README.md)
- API docs: http://localhost:8000/docs
- Main README: [README.md](README.md)

## 🌐 FastAPI Integration

The admin endpoint is also available via FastAPI:

```bash
# Access with basic auth
curl -u admin:admin123 http://localhost:8000/admin
```

This returns info about the Streamlit admin app.

## 💡 Tips

- **Change credentials** before production deployment
- **Use database preview** to verify tournament creation
- **Export tables** to CSV for analysis
- **Check match count** after tournament creation
- **View tournament settings** in tournaments table

Enjoy managing your Ultimate Frisbee tournaments! 🥏

