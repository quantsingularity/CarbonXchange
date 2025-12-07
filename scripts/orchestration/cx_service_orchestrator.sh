#!/bin/bash
# CarbonXchange Service Orchestrator
# A unified tool to manage all services during development
#
# Features:
# - Start/stop all services with proper dependency ordering
# - Monitor service health
# - View logs from all services
# - Restart individual services
# - Graceful shutdown

set -euo pipefail # Exit on error, treat unset variables as error, and fail if any command in a pipeline fails

# ANSI color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Project root (assuming script is in a subdirectory of the project)
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Component directories
BACKEND_DIR="$PROJECT_ROOT/code/backend"
BLOCKCHAIN_DIR="$PROJECT_ROOT/code/blockchain"
WEB_FRONTEND_DIR="$PROJECT_ROOT/code/web-frontend"
MOBILE_FRONTEND_DIR="$PROJECT_ROOT/mobile-frontend"

# Log directory
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

# PID file directory
PID_DIR="$PROJECT_ROOT/.pids"
mkdir -p "$PID_DIR"

# Service ports
BACKEND_PORT=5000
WEB_FRONTEND_PORT=3000
BLOCKCHAIN_PORT=8545
MOBILE_FRONTEND_PORT=19000

# Function to log messages
log() {
    local level="$1"
    local message="$2"
    local color="$NC"

    case "$level" in
        "INFO") color="$GREEN" ;;
        "WARNING") color="$YELLOW" ;;
        "ERROR") color="$RED" ;;
        "STEP") color="$BLUE" ;;
    esac

    echo -e "${color}[$level] $message${NC}" >&2
}

# Function to check if a port is in use
check_port() {
    # Check if lsof is available, otherwise use netstat (less reliable)
    if command -v lsof >/dev/null 2>&1; then
        lsof -Pi :"$1" -sTCP:LISTEN -t >/dev/null
    elif command -v netstat >/dev/null 2>&1; then
        netstat -tuln | grep ":$1\s" >/dev/null
    else
        log "WARNING" "Neither lsof nor netstat found. Cannot reliably check port $1."
        return 1
    fi
}

# Function to check if a service is running
is_service_running() {
    local service="$1"
    local pid_file="$PID_DIR/$service.pid"

    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null; then
            return 0 # Running
        else
            # PID file exists but process is not running, clean up
            rm -f "$pid_file"
        fi
    fi

    return 1 # Not running
}

# Function to start backend service
start_backend() {
    log "STEP" "Starting backend service..."

    if is_service_running "backend"; then
        log "INFO" "Backend service is already running"
        return 0
    fi

    if check_port "$BACKEND_PORT"; then
        log "ERROR" "Port $BACKEND_PORT is already in use"
        return 1
    fi

    if [ ! -d "$BACKEND_DIR" ]; then
        log "ERROR" "Backend directory not found at $BACKEND_DIR"
        return 1
    fi

    # Activate virtual environment in a subshell to avoid polluting the main script's environment
    (
        set +u # Allow unset variables in the subshell for source command
        source "$PROJECT_ROOT/venv/bin/activate"
        set -u
        log "INFO" "Starting backend server on port $BACKEND_PORT..."
        # Use gunicorn or a more robust server for production, but sticking to python app.py for dev
        # Redirecting output to log file
        cd "$BACKEND_DIR"
        python app.py > "$LOG_DIR/backend.log" 2>&1 &
        echo $! > "$PID_DIR/backend.pid"
    )

    local pid
    pid=$(cat "$PID_DIR/backend.pid")

    # Wait for backend to initialize
    log "INFO" "Waiting for backend to initialize (PID: $pid)..."
    local max_attempts=30
    local attempt=1

    while [ "$attempt" -le "$max_attempts" ]; do
        if curl -s -f http://localhost:"$BACKEND_PORT"/api/health > /dev/null; then
            log "INFO" "Backend is ready!"
            return 0
        fi

        if ! ps -p "$pid" > /dev/null; then
            log "ERROR" "Backend process died. Check logs at $LOG_DIR/backend.log"
            rm -f "$PID_DIR/backend.pid"
            return 1
        fi

        if [ "$attempt" -eq "$max_attempts" ]; then
            log "ERROR" "Backend failed to start within $max_attempts seconds"
            kill "$pid" 2>/dev/null || true
            rm -f "$PID_DIR/backend.pid"
            return 1
        fi

        sleep 1
        attempt=$((attempt+1))
    done
}

# Function to start blockchain service (assuming hardhat node)
start_blockchain() {
    log "STEP" "Starting blockchain service..."

    if is_service_running "blockchain"; then
        log "INFO" "Blockchain service is already running"
        return 0
    fi

    if check_port "$BLOCKCHAIN_PORT"; then
        log "ERROR" "Port $BLOCKCHAIN_PORT is already in use"
        return 1
    fi

    if [ ! -d "$BLOCKCHAIN_DIR" ]; then
        log "ERROR" "Blockchain directory not found at $BLOCKCHAIN_DIR"
        return 1
    fi

    log "INFO" "Starting local blockchain on port $BLOCKCHAIN_PORT..."
    (
        cd "$BLOCKCHAIN_DIR"
        # Using npx to ensure the local hardhat is used
        npx hardhat node > "$LOG_DIR/blockchain.log" 2>&1 &
        echo $! > "$PID_DIR/blockchain.pid"
    )

    local pid
    pid=$(cat "$PID_DIR/blockchain.pid")

    # Wait for blockchain to initialize (simple port check)
    log "INFO" "Waiting for blockchain to initialize (PID: $pid)..."
    local max_attempts=10
    local attempt=1

    while [ "$attempt" -le "$max_attempts" ]; do
        if check_port "$BLOCKCHAIN_PORT"; then
            log "INFO" "Blockchain is ready!"
            return 0
        fi

        if ! ps -p "$pid" > /dev/null; then
            log "ERROR" "Blockchain process died. Check logs at $LOG_DIR/blockchain.log"
            rm -f "$PID_DIR/blockchain.pid"
            return 1
        fi

        if [ "$attempt" -eq "$max_attempts" ]; then
            log "ERROR" "Blockchain failed to start within $max_attempts seconds"
            kill "$pid" 2>/dev/null || true
            rm -f "$PID_DIR/blockchain.pid"
            return 1
        fi

        sleep 1
        attempt=$((attempt+1))
    done
}

# Function to start web frontend service
start_web_frontend() {
    log "STEP" "Starting web frontend service..."

    if is_service_running "web_frontend"; then
        log "INFO" "Web frontend service is already running"
        return 0
    fi

    if check_port "$WEB_FRONTEND_PORT"; then
        log "ERROR" "Port $WEB_FRONTEND_PORT is already in use"
        return 1
    fi

    if [ ! -d "$WEB_FRONTEND_DIR" ]; then
        log "ERROR" "Web frontend directory not found at $WEB_FRONTEND_DIR"
        return 1
    fi

    log "INFO" "Starting web frontend on port $WEB_FRONTEND_PORT..."
    (
        cd "$WEB_FRONTEND_DIR"
        # Assuming 'npm start' runs the dev server (e.g., Vite/Webpack dev server)
        npm start > "$LOG_DIR/web_frontend.log" 2>&1 &
        echo $! > "$PID_DIR/web_frontend.pid"
    )

    local pid
    pid=$(cat "$PID_DIR/web_frontend.pid")

    # Wait for web frontend to initialize (simple port check)
    log "INFO" "Waiting for web frontend to initialize (PID: $pid)..."
    local max_attempts=30
    local attempt=1

    while [ "$attempt" -le "$max_attempts" ]; do
        if curl -s -f http://localhost:"$WEB_FRONTEND_PORT" > /dev/null; then
            log "INFO" "Web frontend is ready!"
            return 0
        fi

        if ! ps -p "$pid" > /dev/null; then
            log "ERROR" "Web frontend process died. Check logs at $LOG_DIR/web_frontend.log"
            rm -f "$PID_DIR/web_frontend.pid"
            return 1
        fi

        if [ "$attempt" -eq "$max_attempts" ]; then
            log "ERROR" "Web frontend failed to start within $max_attempts seconds"
            kill "$pid" 2>/dev/null || true
            rm -f "$PID_DIR/web_frontend.pid"
            return 1
        fi

        sleep 1
        attempt=$((attempt+1))
    done
}

# Function to start mobile frontend service
start_mobile_frontend() {
    log "STEP" "Starting mobile frontend service..."

    if is_service_running "mobile_frontend"; then
        log "INFO" "Mobile frontend service is already running"
        return 0
    fi

    if check_port "$MOBILE_FRONTEND_PORT"; then
        log "ERROR" "Port $MOBILE_FRONTEND_PORT is already in use"
        return 1
    fi

    if [ ! -d "$MOBILE_FRONTEND_DIR" ]; then
        log "ERROR" "Mobile frontend directory not found at $MOBILE_FRONTEND_DIR"
        return 1
    fi

    log "INFO" "Starting mobile frontend on port $MOBILE_FRONTEND_PORT..."
    (
        cd "$MOBILE_FRONTEND_DIR"
        # Assuming 'expo start' runs the dev server
        expo start > "$LOG_DIR/mobile_frontend.log" 2>&1 &
        echo $! > "$PID_DIR/mobile_frontend.pid"
    )

    local pid
    pid=$(cat "$PID_DIR/mobile_frontend.pid")

    # Wait for mobile frontend to initialize (simple port check)
    log "INFO" "Waiting for mobile frontend to initialize (PID: $pid)..."
    local max_attempts=30
    local attempt=1

    while [ "$attempt" -le "$max_attempts" ]; do
        if check_port "$MOBILE_FRONTEND_PORT"; then
            log "INFO" "Mobile frontend is ready!"
            return 0
        fi

        if ! ps -p "$pid" > /dev/null; then
            log "ERROR" "Mobile frontend process died. Check logs at $LOG_DIR/mobile_frontend.log"
            rm -f "$PID_DIR/mobile_frontend.pid"
            return 1
        fi

        if [ "$attempt" -eq "$max_attempts" ]; then
            log "ERROR" "Mobile frontend failed to start within $max_attempts seconds"
            kill "$pid" 2>/dev/null || true
            rm -f "$PID_DIR/mobile_frontend.pid"
            return 1
        fi

        sleep 1
        attempt=$((attempt+1))
    done
}

# Function to stop a service
stop_service() {
    local service="$1"
    local pid_file="$PID_DIR/$service.pid"

    if [ ! -f "$pid_file" ]; then
        log "WARNING" "$service service is not running (PID file not found)"
        return 0
    fi

    local pid
    pid=$(cat "$pid_file")

    if ! ps -p "$pid" > /dev/null; then
        log "WARNING" "$service service is not running (PID $pid not found), cleaning up PID file."
        rm -f "$pid_file"
        return 0
    fi

    log "INFO" "Stopping $service service (PID: $pid)..."

    # Send SIGTERM for graceful shutdown
    kill "$pid" 2>/dev/null || true

    # Wait for process to terminate
    local max_attempts=10
    local attempt=1

    while [ "$attempt" -le "$max_attempts" ]; do
        if ! ps -p "$pid" > /dev/null; then
            log "INFO" "$service service stopped"
            rm -f "$pid_file"
            return 0
        fi

        sleep 1
        attempt=$((attempt+1))
    done

    # If process is still running, force kill with SIGKILL
    log "WARNING" "$service service (PID: $pid) did not stop gracefully, sending SIGKILL."
    kill -9 "$pid" 2>/dev/null || true
    rm -f "$pid_file"
    log "INFO" "$service service forcefully stopped"
    return 0
}

# Function to start all services in dependency order
start_all() {
    log "STEP" "Starting all CarbonXchange services..."
    # Dependency order: Blockchain -> Backend -> Web Frontend -> Mobile Frontend
    start_blockchain
    start_backend
    start_web_frontend
    start_mobile_frontend
    log "INFO" "All services started. Check individual logs for status."
}

# Function to stop all services in reverse dependency order
stop_all() {
    log "STEP" "Stopping all CarbonXchange services..."
    # Reverse dependency order: Mobile Frontend -> Web Frontend -> Backend -> Blockchain
    stop_service "mobile_frontend"
    stop_service "web_frontend"
    stop_service "backend"
    stop_service "blockchain"
    log "INFO" "All services stopped."
}

# Function to restart a service
restart_service() {
    local service="$1"
    stop_service "$service"
    case "$service" in
        "backend") start_backend ;;
        "blockchain") start_blockchain ;;
        "web_frontend") start_web_frontend ;;
        "mobile_frontend") start_mobile_frontend ;;
        *) log "ERROR" "Unknown service: $service" ;;
    esac
}

# Function to view logs
view_logs() {
    local service="$1"
    local log_file="$LOG_DIR/$service.log"

    if [ ! -f "$log_file" ]; then
        log "ERROR" "Log file not found for $service at $log_file"
        return 1
    fi

    log "INFO" "Displaying logs for $service (Press Ctrl+C to exit tail)..."
    tail -f "$log_file"
}

# Function to display usage
usage() {
    echo -e "${BLUE}Usage: $0 <command> [service]${NC}"
    echo ""
    echo "Commands:"
    echo "  start [service]       Start all services or a specific service (backend, blockchain, web_frontend, mobile_frontend)."
    echo "  stop [service]        Stop all services or a specific service."
    echo "  restart <service>     Restart a specific service."
    echo "  status                Check the running status of all services."
    echo "  logs <service>        View the live logs of a specific service."
    echo "  --help                Display this help message."
    echo ""
    echo "Example: $0 start"
    echo "Example: $0 restart backend"
}

# Main script logic
if [ $# -eq 0 ]; then
    usage
    exit 1
fi

COMMAND="$1"
SERVICE="${2:-}"

case "$COMMAND" in
    "start")
        if [ -z "$SERVICE" ]; then
            start_all
        else
            case "$SERVICE" in
                "backend") start_backend ;;
                "blockchain") start_blockchain ;;
                "web_frontend") start_web_frontend ;;
                "mobile_frontend") start_mobile_frontend ;;
                *) log "ERROR" "Unknown service: $SERVICE"; usage; exit 1 ;;
            esac
        fi
        ;;
    "stop")
        if [ -z "$SERVICE" ]; then
            stop_all
        else
            case "$SERVICE" in
                "backend") stop_service "backend" ;;
                "blockchain") stop_service "blockchain" ;;
                "web_frontend") stop_service "web_frontend" ;;
                "mobile_frontend") stop_service "mobile_frontend" ;;
                *) log "ERROR" "Unknown service: $SERVICE"; usage; exit 1 ;;
            esac
        fi
        ;;
    "restart")
        if [ -z "$SERVICE" ]; then
            log "ERROR" "Restart command requires a service name."
            usage
            exit 1
        else
            restart_service "$SERVICE"
        fi
        ;;
    "status")
        log "STEP" "Checking service status..."
        is_service_running "backend" && log "INFO" "Backend: RUNNING (PID: $(cat "$PID_DIR/backend.pid"))" || log "WARNING" "Backend: STOPPED"
        is_service_running "blockchain" && log "INFO" "Blockchain: RUNNING (PID: $(cat "$PID_DIR/blockchain.pid"))" || log "WARNING" "Blockchain: STOPPED"
        is_service_running "web_frontend" && log "INFO" "Web Frontend: RUNNING (PID: $(cat "$PID_DIR/web_frontend.pid"))" || log "WARNING" "Web Frontend: STOPPED"
        is_service_running "mobile_frontend" && log "INFO" "Mobile Frontend: RUNNING (PID: $(cat "$PID_DIR/mobile_frontend.pid"))" || log "WARNING" "Mobile Frontend: STOPPED"
        ;;
    "logs")
        if [ -z "$SERVICE" ]; then
            log "ERROR" "Logs command requires a service name."
            usage
            exit 1
        else
            view_logs "$SERVICE"
        fi
        ;;
    "--help"|"-h")
        usage
        ;;
    *)
        log "ERROR" "Unknown command: $COMMAND"
        usage
        exit 1
        ;;
esac
