#!/bin/bash

# Blockchain Compile Script
# This script runs truffle compile for the Solidity contracts.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
BLOCKCHAIN_DIR="$SCRIPT_DIR"

echo "Compiling blockchain contracts in $BLOCKCHAIN_DIR..."

cd "$BLOCKCHAIN_DIR"

# Check if truffle is installed
if ! command -v truffle &> /dev/null; then
    echo "Error: Truffle is not installed. Please install Truffle globally (e.g., npm install -g truffle) or ensure it's in your PATH."
    echo "You can also run the main setup script: setup_carbonxchange_env.sh"
    exit 1
fi

truffle compile

COMPILE_EXIT_CODE=$?

if [ $COMPILE_EXIT_CODE -eq 0 ]; then
    echo "Blockchain contracts compiled successfully."
else
    echo "Blockchain contracts compilation failed. Exit code: $COMPILE_EXIT_CODE"
fi

exit $COMPILE_EXIT_CODE

