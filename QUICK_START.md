# Quick Start Guide

## 🚀 First Time Setup (Run Once)

```bash
cd /home/kuba/dev/new-scores
./setup.sh
```

This will:
- ✅ Check prerequisites (Python 3, Node.js, npm)
- ✅ Create Python virtual environment
- ✅ Install all backend dependencies
- ✅ Install all frontend dependencies  
- ✅ Initialize database with sample data
- ✅ Create configuration files

**Time**: ~5-10 minutes depending on internet speed

---

## 🎮 Daily Development

### Start All Services
```bash
./start-all-simple.sh
```

**Wait 30-60 seconds**, then open in browser:
- 🌐 **Frontend**: http://localhost:3000
- 🔌 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- ⚙️ **Admin Panel**: http://localhost:8501

### Stop All Services
Press `Ctrl+C` in the terminal running start-all-simple.sh

OR run:
```bash
./stop-all.sh
```

---

## 📝 Logs

View logs in real-time:
```bash
tail -f logs/backend.log
tail -f logs/frontend.log
tail -f logs/admin.log
```

---

## 🧪 Run Tests

### Frontend Tests
```bash
cd scores-web
npm run test
npm run lint
```

### Backend Tests
```bash
cd scores-server
source venv/bin/activate
pytest
```

---

## 🔑 Admin Login

**URL**: http://localhost:8501

**Default Credentials**:
- Username: `admin`
- Password: `admin123`

⚠️ **Change these in production!**

---

## 📚 Documentation

- **README.md** - Project overview
- **docs/API_CONTRACTS.md** - API documentation
- **docs/ARCHITECTURE.md** - System architecture
- **docs/ADMIN_GUIDE.md** - Admin panel guide
- **CONSOLIDATED_SUMMARY.md** - Detailed consolidation info

---

## 🐛 Troubleshooting

### Services won't start
```bash
./stop-all.sh
./setup.sh
./start-all-simple.sh
```

### Reset database
```bash
cd scores-server
rm scores.db
source venv/bin/activate
alembic upgrade head
python3 -m src.scripts.seed_data
```

### Port already in use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Clear frontend cache
```bash
cd scores-web
rm -rf .next node_modules/.cache
npm run dev
```

---

## 💡 Development Tips

1. **Auto-reload** is enabled for all services - just save files!
2. **Hot Module Replacement** works in Next.js frontend
3. Check **logs/** directory when debugging
4. Use **Ctrl+C** to gracefully shutdown all services
5. Backend API has **interactive docs** at /docs endpoint

---

## 🎯 Common Tasks

### View tournament data
```bash
cd scores-server
source venv/bin/activate
python3 -c "from src.database import *; import asyncio; asyncio.run(init_db())"
sqlite3 scores.db "SELECT * FROM tournaments;"
```

### Create migration
```bash
cd scores-server
source venv/bin/activate
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Add new package
```bash
# Frontend
cd scores-web
npm install package-name

# Backend
cd scores-server
source venv/bin/activate
pip install package-name
pip freeze > requirements.txt
```

---

**Need Help?** Check the full documentation in the `docs/` directory!

