#!/bin/bash

# CarbonXchange Development Run Script
# A simple wrapper to start all development services using the service orchestrator.

set -euo pipefail

# ANSI color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory and Project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Path to the service orchestrator script
ORCHESTRATOR_SCRIPT="$SCRIPT_DIR/cx_service_orchestrator.sh"

# Function to log messages
log() {
    local level=$1
    local message=$2
    local color=$NC

    case $level in
        "INFO") color=$GREEN ;;
        "ERROR") color=$RED ;;
        "STEP") color=$BLUE ;;
    esac

    echo -e "${color}[$level] $message${NC}" >&2
}

# Check if the orchestrator script exists
if [ ! -f "$ORCHESTRATOR_SCRIPT" ]; then
    log "ERROR" "Service orchestrator script not found at $ORCHESTRATOR_SCRIPT. Please check your scripts directory."
    exit 1
fi

log "STEP" "Starting CarbonXchange development environment..."

# Execute the orchestrator's start command
"$ORCHESTRATOR_SCRIPT" start

# Check the exit code of the orchestrator
if [ $? -eq 0 ]; then
    log "INFO" "CarbonXchange services are running. Access the application at: http://localhost:3000"
    log "INFO" "Press Ctrl+C to stop all services."

    # The orchestrator script should handle the wait and cleanup, but for a simple wrapper,
    # we can add a trap here to ensure the orchestrator's stop command is called on Ctrl+C.
    function cleanup {
        log "STEP" "Stopping CarbonXchange services..."
        "$ORCHESTRATOR_SCRIPT" stop
        exit 0
    }

    trap cleanup SIGINT SIGTERM

    # Keep the script running to wait for the user to press Ctrl+C
    wait
else
    log "ERROR" "Failed to start CarbonXchange services. Check the logs for details."
    exit 1
fi
