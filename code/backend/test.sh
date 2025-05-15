#!/bin/bash

# Backend Test Script
# This script runs pytest for the backend application.

# Navigate to the backend directory if the script is run from the project root
# or if it's already in the backend directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
BACKEND_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(cd "$BACKEND_DIR/../.." &> /dev/null && pwd)"

echo "Running backend tests..."

# Activate virtual environment
# The venv is expected to be in the project root directory (e.g., CarbonXchange/venv)
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo "Activating virtual environment from $PROJECT_ROOT/venv..."
    source "$PROJECT_ROOT/venv/bin/activate"
else
    echo "Warning: Virtual environment not found at $PROJECT_ROOT/venv. Attempting to run tests with system Python."
    echo "It is recommended to run the setup_carbonxchange_env.sh script first."
fi

# Run pytest
# Pytest will automatically discover tests in the 'tests' directory
cd "$BACKEND_DIR"
echo "Executing pytest in $(pwd)..."
python3 -m pytest tests

TEST_EXIT_CODE=$?

# Deactivate virtual environment if it was activated
if [ -d "$PROJECT_ROOT/venv" ]; then
    deactivate
fi

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "Backend tests passed successfully."
else
    echo "Backend tests failed. Exit code: $TEST_EXIT_CODE"
fi

exit $TEST_EXIT_CODE

