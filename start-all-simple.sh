#!/bin/bash

# Simple startup script for Ultimate Frisbee Scores System
# Prerequisites: Backend venv must be set up with: cd scores-server && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
# Prerequisites: Frontend dependencies must be installed with: cd scores-web && npm install

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "═══════════════════════════════════════════════════════════"
echo "  Ultimate Frisbee Scores System - Starting All Services   "
echo "═══════════════════════════════════════════════════════════"
echo ""

# Create logs directory
mkdir -p logs

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping all services..."
    pkill -f "uvicorn src.main:app" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true
    pkill -f "streamlit run admin_app.py" 2>/dev/null || true
    echo "All services stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
echo "[1/3] Starting Backend API (port 8000)..."
cd "$SCRIPT_DIR/scores-server"
source venv/bin/activate
nohup uvicorn src.main:app --reload --port 8000 > ../logs/backend.log 2>&1 &
echo "      Backend starting... (PID: $!)"

# Start Frontend
echo "[2/3] Starting Frontend Web (port 3000)..."
cd "$SCRIPT_DIR/scores-web"
nohup npm run dev > ../logs/frontend.log 2>&1 &
echo "      Frontend starting... (PID: $!)"

# Start Admin
echo "[3/3] Starting Admin Panel (port 8501)..."
cd "$SCRIPT_DIR/scores-server"
source venv/bin/activate
nohup streamlit run admin_app.py --server.port 8501 --server.headless true > ../logs/admin.log 2>&1 &
echo "      Admin panel starting... (PID: $!)"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Services are starting up... Please wait 30-60 seconds"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📍 URLs:"
echo "   Frontend:    http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo "   Admin Panel: http://localhost:8501"
echo ""
echo "📝 Logs:"
echo "   Backend:  $SCRIPT_DIR/logs/backend.log"
echo "   Frontend: $SCRIPT_DIR/logs/frontend.log"
echo "   Admin:    $SCRIPT_DIR/logs/admin.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep script running
tail -f logs/backend.log logs/frontend.log logs/admin.log 2>/dev/null || sleep infinity

