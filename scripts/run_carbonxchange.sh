#!/bin/bash

# Run script for CarbonXchange project
# This script starts both the backend and frontend components

# Colors for terminal output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${RED}Error: Port $1 is already in use${NC}"
        exit 1
    fi
}

# Function to handle errors
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    exit 1
}

echo -e "${BLUE}Starting CarbonXchange application...${NC}"

# Check if required ports are available
check_port 3000
check_port 5000

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating Python virtual environment...${NC}"
    python3 -m venv venv || handle_error "Failed to create virtual environment"
fi

# Start backend server
echo -e "${BLUE}Starting backend server...${NC}"
cd code/backend || handle_error "Failed to change to backend directory"
source ../../venv/bin/activate || handle_error "Failed to activate virtual environment"
pip install -r requirements.txt > /dev/null || handle_error "Failed to install Python dependencies"

# Start backend in background and capture PID
python app.py &
BACKEND_PID=$!

# Wait for backend to initialize
echo -e "${BLUE}Waiting for backend to initialize...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:5000/api/health > /dev/null; then
        echo -e "${GREEN}Backend is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Backend failed to start within 30 seconds${NC}"
        kill $BACKEND_PID
        exit 1
    fi
    sleep 1
done

# Start frontend
echo -e "${BLUE}Starting frontend...${NC}"
cd ../web-frontend || handle_error "Failed to change to frontend directory"
npm install > /dev/null || handle_error "Failed to install Node.js dependencies"
npm start &
FRONTEND_PID=$!

# Wait for frontend to initialize
echo -e "${BLUE}Waiting for frontend to initialize...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null; then
        echo -e "${GREEN}Frontend is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Frontend failed to start within 30 seconds${NC}"
        kill $FRONTEND_PID
        kill $BACKEND_PID
        exit 1
    fi
    sleep 1
done

echo -e "${GREEN}CarbonXchange application is running!${NC}"
echo -e "${GREEN}Backend running with PID: ${BACKEND_PID}${NC}"
echo -e "${GREEN}Frontend running with PID: ${FRONTEND_PID}${NC}"
echo -e "${GREEN}Access the application at: http://localhost:3000${NC}"
echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"

# Handle graceful shutdown
function cleanup {
    echo -e "${BLUE}Stopping services...${NC}"
    kill $FRONTEND_PID 2>/dev/null
    kill $BACKEND_PID 2>/dev/null
    echo -e "${GREEN}All services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep script running
wait
