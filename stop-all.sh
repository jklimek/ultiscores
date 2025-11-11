#!/bin/bash

# Ultimate Frisbee Scores System - Stop All Services Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$LOG_DIR/pids.txt"

echo -e "${YELLOW}Stopping all services...${NC}"

# Kill processes from PID file
if [ -f "$PID_FILE" ]; then
    while IFS= read -r pid; do
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${GREEN}Stopping process $pid${NC}"
            kill "$pid" 2>/dev/null || true
        fi
    done < "$PID_FILE"
    rm "$PID_FILE"
fi

# Kill any remaining processes by name
echo -e "${YELLOW}Cleaning up any remaining processes...${NC}"
pkill -f "uvicorn src.main:app" 2>/dev/null && echo -e "${GREEN}Stopped backend${NC}" || true
pkill -f "next dev" 2>/dev/null && echo -e "${GREEN}Stopped frontend${NC}" || true
pkill -f "streamlit run admin_app.py" 2>/dev/null && echo -e "${GREEN}Stopped admin panel${NC}" || true

echo -e "${GREEN}All services stopped!${NC}"

