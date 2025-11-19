#!/bin/bash

# Blockchain Test Script
# This script runs truffle test for the Solidity contracts.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
BLOCKCHAIN_DIR="$SCRIPT_DIR"

echo "Running blockchain tests in $BLOCKCHAIN_DIR..."

cd "$BLOCKCHAIN_DIR"

# Check if truffle is installed
if ! command -v truffle &> /dev/null; then
    echo "Error: Truffle is not installed. Please install Truffle globally (e.g., npm install -g truffle) or ensure it's in your PATH."
    echo "You can also run the main setup script: setup_carbonxchange_env.sh"
    exit 1
fi

truffle test

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "Blockchain tests passed successfully."
else
    echo "Blockchain tests failed. Exit code: $TEST_EXIT_CODE"
fi

exit $TEST_EXIT_CODE
