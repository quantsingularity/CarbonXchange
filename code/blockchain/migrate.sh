#!/bin/bash

# Blockchain Migrate Script
# This script runs truffle migrate for the Solidity contracts.
# It can optionally reset the migration history.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
BLOCKCHAIN_DIR="$SCRIPT_DIR"

echo "Migrating blockchain contracts in $BLOCKCHAIN_DIR..."

cd "$BLOCKCHAIN_DIR"

# Check if truffle is installed
if ! command -v truffle &> /dev/null; then
    echo "Error: Truffle is not installed. Please install Truffle globally (e.g., npm install -g truffle) or ensure it's in your PATH."
    echo "You can also run the main setup script: setup_carbonxchange_env.sh"
    exit 1
fi

# Check for --reset flag
if [ "$1" == "--reset" ]; then
    echo "Resetting migrations..."
    truffle migrate --reset
else
    truffle migrate
fi

MIGRATE_EXIT_CODE=$?

if [ $MIGRATE_EXIT_CODE -eq 0 ]; then
    echo "Blockchain contracts migrated successfully."
else
    echo "Blockchain contracts migration failed. Exit code: $MIGRATE_EXIT_CODE"
fi

exit $MIGRATE_EXIT_CODE

