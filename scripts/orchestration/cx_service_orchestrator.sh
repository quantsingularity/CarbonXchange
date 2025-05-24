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

set -e

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
    local level=$1
    local message=$2
    local color=$NC
    
    case $level in
        "INFO") color=$GREEN ;;
        "WARNING") color=$YELLOW ;;
        "ERROR") color=$RED ;;
        "STEP") color=$BLUE ;;
    esac
    
    echo -e "${color}[$level] $message${NC}"
}

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to check if a service is running
is_service_running() {
    local service=$1
    local pid_file="$PID_DIR/$service.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null; then
            return 0
        else
            # PID file exists but process is not running
            rm "$pid_file"
        fi
    fi
    
    return 1
}

# Function to start backend service
start_backend() {
    log "STEP" "Starting backend service..."
    
    if is_service_running "backend"; then
        log "INFO" "Backend service is already running"
        return 0
    fi
    
    if check_port $BACKEND_PORT; then
        log "ERROR" "Port $BACKEND_PORT is already in use"
        return 1
    fi
    
    if [ ! -d "$BACKEND_DIR" ]; then
        log "ERROR" "Backend directory not found at $BACKEND_DIR"
        return 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Activate virtual environment
    source "$PROJECT_ROOT/venv/bin/activate"
    
    # Start backend in background
    log "INFO" "Starting backend server on port $BACKEND_PORT..."
    python app.py > "$LOG_DIR/backend.log" 2>&1 &
    local pid=$!
    
    # Save PID
    echo $pid > "$PID_DIR/backend.pid"
    
    # Wait for backend to initialize
    log "INFO" "Waiting for backend to initialize..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$BACKEND_PORT/api/health > /dev/null; then
            log "INFO" "Backend is ready!"
            break
        fi
        
        if ! ps -p $pid > /dev/null; then
            log "ERROR" "Backend process died. Check logs at $LOG_DIR/backend.log"
            rm "$PID_DIR/backend.pid" 2>/dev/null
            return 1
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log "ERROR" "Backend failed to start within $max_attempts seconds"
            kill $pid 2>/dev/null
            rm "$PID_DIR/backend.pid" 2>/dev/null
            return 1
        fi
        
        sleep 1
        attempt=$((attempt+1))
    done
    
    log "INFO" "Backend service started with PID $pid"
    return 0
}

# Function to start blockchain service
start_blockchain() {
    log "STEP" "Starting blockchain service..."
    
    if is_service_running "blockchain"; then
        log "INFO" "Blockchain service is already running"
        return 0
    fi
    
    if check_port $BLOCKCHAIN_PORT; then
        log "ERROR" "Port $BLOCKCHAIN_PORT is already in use"
        return 1
    fi
    
    if [ ! -d "$BLOCKCHAIN_DIR" ]; then
        log "ERROR" "Blockchain directory not found at $BLOCKCHAIN_DIR"
        return 1
    fi
    
    cd "$BLOCKCHAIN_DIR"
    
    # Start local blockchain
    log "INFO" "Starting local blockchain on port $BLOCKCHAIN_PORT..."
    npx hardhat node > "$LOG_DIR/blockchain.log" 2>&1 &
    local pid=$!
    
    # Save PID
    echo $pid > "$PID_DIR/blockchain.pid"
    
    # Wait for blockchain to initialize
    log "INFO" "Waiting for blockchain to initialize..."
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if check_port $BLOCKCHAIN_PORT; then
            log "INFO" "Blockchain is ready!"
            break
        fi
        
        if ! ps -p $pid > /dev/null; then
            log "ERROR" "Blockchain process died. Check logs at $LOG_DIR/blockchain.log"
            rm "$PID_DIR/blockchain.pid" 2>/dev/null
            return 1
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log "ERROR" "Blockchain failed to start within $max_attempts seconds"
            kill $pid 2>/dev/null
            rm "$PID_DIR/blockchain.pid" 2>/dev/null
            return 1
        fi
        
        sleep 1
        attempt=$((attempt+1))
    done
    
    log "INFO" "Blockchain service started with PID $pid"
    return 0
}

# Function to start web frontend service
start_web_frontend() {
    log "STEP" "Starting web frontend service..."
    
    if is_service_running "web_frontend"; then
        log "INFO" "Web frontend service is already running"
        return 0
    fi
    
    if check_port $WEB_FRONTEND_PORT; then
        log "ERROR" "Port $WEB_FRONTEND_PORT is already in use"
        return 1
    fi
    
    if [ ! -d "$WEB_FRONTEND_DIR" ]; then
        log "ERROR" "Web frontend directory not found at $WEB_FRONTEND_DIR"
        return 1
    fi
    
    cd "$WEB_FRONTEND_DIR"
    
    # Start web frontend in background
    log "INFO" "Starting web frontend on port $WEB_FRONTEND_PORT..."
    npm start > "$LOG_DIR/web_frontend.log" 2>&1 &
    local pid=$!
    
    # Save PID
    echo $pid > "$PID_DIR/web_frontend.pid"
    
    # Wait for web frontend to initialize
    log "INFO" "Waiting for web frontend to initialize..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$WEB_FRONTEND_PORT > /dev/null; then
            log "INFO" "Web frontend is ready!"
            break
        fi
        
        if ! ps -p $pid > /dev/null; then
            log "ERROR" "Web frontend process died. Check logs at $LOG_DIR/web_frontend.log"
            rm "$PID_DIR/web_frontend.pid" 2>/dev/null
            return 1
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log "ERROR" "Web frontend failed to start within $max_attempts seconds"
            kill $pid 2>/dev/null
            rm "$PID_DIR/web_frontend.pid" 2>/dev/null
            return 1
        fi
        
        sleep 1
        attempt=$((attempt+1))
    done
    
    log "INFO" "Web frontend service started with PID $pid"
    return 0
}

# Function to start mobile frontend service
start_mobile_frontend() {
    log "STEP" "Starting mobile frontend service..."
    
    if is_service_running "mobile_frontend"; then
        log "INFO" "Mobile frontend service is already running"
        return 0
    fi
    
    if check_port $MOBILE_FRONTEND_PORT; then
        log "ERROR" "Port $MOBILE_FRONTEND_PORT is already in use"
        return 1
    fi
    
    if [ ! -d "$MOBILE_FRONTEND_DIR" ]; then
        log "ERROR" "Mobile frontend directory not found at $MOBILE_FRONTEND_DIR"
        return 1
    fi
    
    cd "$MOBILE_FRONTEND_DIR"
    
    # Start mobile frontend in background
    log "INFO" "Starting mobile frontend on port $MOBILE_FRONTEND_PORT..."
    expo start > "$LOG_DIR/mobile_frontend.log" 2>&1 &
    local pid=$!
    
    # Save PID
    echo $pid > "$PID_DIR/mobile_frontend.pid"
    
    # Wait for mobile frontend to initialize
    log "INFO" "Waiting for mobile frontend to initialize..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if check_port $MOBILE_FRONTEND_PORT; then
            log "INFO" "Mobile frontend is ready!"
            break
        fi
        
        if ! ps -p $pid > /dev/null; then
            log "ERROR" "Mobile frontend process died. Check logs at $LOG_DIR/mobile_frontend.log"
            rm "$PID_DIR/mobile_frontend.pid" 2>/dev/null
            return 1
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log "ERROR" "Mobile frontend failed to start within $max_attempts seconds"
            kill $pid 2>/dev/null
            rm "$PID_DIR/mobile_frontend.pid" 2>/dev/null
            return 1
        fi
        
        sleep 1
        attempt=$((attempt+1))
    done
    
    log "INFO" "Mobile frontend service started with PID $pid"
    return 0
}

# Function to stop a service
stop_service() {
    local service=$1
    local pid_file="$PID_DIR/$service.pid"
    
    if [ ! -f "$pid_file" ]; then
        log "WARNING" "$service service is not running"
        return 0
    fi
    
    local pid=$(cat "$pid_file")
    
    log "INFO" "Stopping $service service (PID: $pid)..."
    
    # Send SIGTERM to process
    kill $pid 2>/dev/null
    
    # Wait for process to terminate
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if ! ps -p $pid > /dev/null; then
            log "INFO" "$service service stopped"
            rm "$pid_file"
            return 0
        fi
        
        sleep 1
        attempt=$((attempt+1))
    done
    
    # If process is still running, force kill
    log "WARNING" "$service service did not stop gracefully, forcing kill..."
    kill -9 $pid 2>/dev/null
    
    if ! ps -p $pid > /dev/null; then
        log "INFO" "$service service stopped (forced)"
        rm "$pid_file"
        return 0
    else
        log "ERROR" "Failed to stop $service service"
        return 1
    fi
}

# Function to stop all services
stop_all_services() {
    log "STEP" "Stopping all services..."
    
    # Stop in reverse order of dependencies
    stop_service "mobile_frontend"
    stop_service "web_frontend"
    stop_service "backend"
    stop_service "blockchain"
    
    log "INFO" "All services stopped"
}

# Function to check status of all services
check_status() {
    log "STEP" "Checking status of all services..."
    
    local any_running=false
    
    # Check backend
    if is_service_running "backend"; then
        local pid=$(cat "$PID_DIR/backend.pid")
        log "INFO" "Backend service is running (PID: $pid)"
        any_running=true
    else
        log "INFO" "Backend service is not running"
    fi
    
    # Check blockchain
    if is_service_running "blockchain"; then
        local pid=$(cat "$PID_DIR/blockchain.pid")
        log "INFO" "Blockchain service is running (PID: $pid)"
        any_running=true
    else
        log "INFO" "Blockchain service is not running"
    fi
    
    # Check web frontend
    if is_service_running "web_frontend"; then
        local pid=$(cat "$PID_DIR/web_frontend.pid")
        log "INFO" "Web frontend service is running (PID: $pid)"
        any_running=true
    else
        log "INFO" "Web frontend service is not running"
    fi
    
    # Check mobile frontend
    if is_service_running "mobile_frontend"; then
        local pid=$(cat "$PID_DIR/mobile_frontend.pid")
        log "INFO" "Mobile frontend service is running (PID: $pid)"
        any_running=true
    else
        log "INFO" "Mobile frontend service is not running"
    fi
    
    if [ "$any_running" = false ]; then
        log "INFO" "No services are currently running"
    fi
}

# Function to view logs
view_logs() {
    local service=$1
    local log_file="$LOG_DIR/$service.log"
    
    if [ ! -f "$log_file" ]; then
        log "ERROR" "Log file for $service not found"
        return 1
    fi
    
    log "INFO" "Showing logs for $service (press Ctrl+C to exit):"
    echo ""
    tail -f "$log_file"
}

# Function to restart a service
restart_service() {
    local service=$1
    
    log "STEP" "Restarting $service service..."
    
    stop_service "$service"
    
    case $service in
        "backend")
            start_backend
            ;;
        "blockchain")
            start_blockchain
            ;;
        "web_frontend")
            start_web_frontend
            ;;
        "mobile_frontend")
            start_mobile_frontend
            ;;
        *)
            log "ERROR" "Unknown service: $service"
            return 1
            ;;
    esac
}

# Function to display help message
show_help() {
    echo "CarbonXchange Service Orchestrator"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  start [service]            Start services (all if no service specified)"
    echo "  stop [service]             Stop services (all if no service specified)"
    echo "  restart [service]          Restart services (all if no service specified)"
    echo "  status                     Check status of all services"
    echo "  logs <service>             View logs for a specific service"
    echo "  help                       Show this help message"
    echo ""
    echo "Services:"
    echo "  backend                    Backend API server"
    echo "  blockchain                 Local blockchain node"
    echo "  web_frontend               Web frontend application"
    echo "  mobile_frontend            Mobile frontend application"
    echo ""
    echo "Examples:"
    echo "  $0 start                   Start all services"
    echo "  $0 start backend           Start only the backend service"
    echo "  $0 stop                    Stop all services"
    echo "  $0 restart web_frontend    Restart the web frontend service"
    echo "  $0 logs backend            View backend logs"
}

# Main function
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    local command=$1
    shift
    
    case $command in
        "start")
            if [ $# -eq 0 ]; then
                # Start all services in dependency order
                start_blockchain
                start_backend
                start_web_frontend
                start_mobile_frontend
                
                log "INFO" "All services started"
                echo ""
                log "INFO" "Access points:"
                log "INFO" "- Backend API: http://localhost:$BACKEND_PORT"
                log "INFO" "- Web Frontend: http://localhost:$WEB_FRONTEND_PORT"
                log "INFO" "- Blockchain Node: http://localhost:$BLOCKCHAIN_PORT"
                log "INFO" "- Mobile Frontend: http://localhost:$MOBILE_FRONTEND_PORT"
            else
                local service=$1
                case $service in
                    "backend")
                        start_backend
                        ;;
                    "blockchain")
                        start_blockchain
                        ;;
                    "web_frontend")
                        start_web_frontend
                        ;;
                    "mobile_frontend")
                        start_mobile_frontend
                        ;;
                    *)
                        log "ERROR" "Unknown service: $service"
                        exit 1
                        ;;
                esac
            fi
            ;;
        "stop")
            if [ $# -eq 0 ]; then
                stop_all_services
            else
                local service=$1
                stop_service "$service"
            fi
            ;;
        "restart")
            if [ $# -eq 0 ]; then
                stop_all_services
                
                # Start all services in dependency order
                start_blockchain
                start_backend
                start_web_frontend
                start_mobile_frontend
                
                log "INFO" "All services restarted"
            else
                local service=$1
                restart_service "$service"
            fi
            ;;
        "status")
            check_status
            ;;
        "logs")
            if [ $# -eq 0 ]; then
                log "ERROR" "Service name required for logs command"
                exit 1
            fi
            
            local service=$1
            view_logs "$service"
            ;;
        "help")
            show_help
            ;;
        *)
            log "ERROR" "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Handle Ctrl+C
trap 'echo -e "\n${YELLOW}Interrupted by user${NC}"; exit 0' INT

# Run main function
main "$@"
