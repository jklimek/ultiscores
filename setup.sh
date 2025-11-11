#!/bin/bash

# Ultimate Frisbee Scores System - Setup Script
# Run this once to set up the development environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "═══════════════════════════════════════════════════════════"
echo "  Ultimate Frisbee Scores System - Setup Script            "
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed"
    exit 1
fi
echo "✓ All prerequisites found"
echo ""

# Setup backend
echo "[1/2] Setting up Backend..."
cd "$SCRIPT_DIR/scores-server"

if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

echo "   Installing Python dependencies..."
./venv/bin/pip install --quiet --upgrade pip
./venv/bin/pip install -r requirements.txt

if [ ! -f "scores.db" ]; then
    echo "   Initializing database..."
    ./venv/bin/alembic upgrade head
    ./venv/bin/python3 -m src.scripts.seed_data
fi

echo "   ✓ Backend setup complete"
echo ""

# Setup frontend
echo "[2/2] Setting up Frontend..."
cd "$SCRIPT_DIR/scores-web"

if [ ! -d "node_modules" ]; then
    echo "   Installing Node.js dependencies..."
    npm install
fi

if [ ! -f ".env.local" ]; then
    echo "   Creating .env.local..."
    cat > .env.local << EOF
NEXT_PUBLIC_USE_API_MOCKS=false
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_LIVE_WS_URL=ws://localhost:8000
EOF
fi

echo "   ✓ Frontend setup complete"
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "  Setup Complete! 🎉"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "To start all services, run:"
echo "   ./start-all-simple.sh"
echo ""
echo "Or start services individually:"
echo "   cd scores-server && source venv/bin/activate && uvicorn src.main:app --reload"
echo "   cd scores-web && npm run dev"
echo "   cd scores-server && source venv/bin/activate && streamlit run admin_app.py"
echo ""

