#!/bin/bash
# Development script to run both backend and frontend

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting MasterDataCleaner development environment...${NC}"

# Start backend in background
echo -e "${BLUE}Starting FastAPI backend on http://localhost:8000${NC}"
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start frontend
echo -e "${BLUE}Starting Vue frontend on http://localhost:3000${NC}"
pnpm dev &
FRONTEND_PID=$!

# Handle shutdown
trap "echo -e '${GREEN}Shutting down...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

# Wait for processes
wait
