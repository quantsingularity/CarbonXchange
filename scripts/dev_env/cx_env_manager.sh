#!/bin/bash
# CarbonXchange Environment Manager
# A comprehensive script to set up, validate, and manage the development environment
#
# Features:
# - Unified environment validation and setup
# - Component-specific setup options
# - Dependency version checking
# - Cross-platform compatibility (Linux, macOS, Windows with WSL)

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

# Log file
LOG_FILE="$PROJECT_ROOT/cx_env_setup.log"

# Component directories
BACKEND_DIR="$PROJECT_ROOT/code/backend"
BLOCKCHAIN_DIR="$PROJECT_ROOT/code/blockchain"
WEB_FRONTEND_DIR="$PROJECT_ROOT/code/web-frontend"
MOBILE_FRONTEND_DIR="$PROJECT_ROOT/mobile-frontend"
AI_MODELS_DIR="$PROJECT_ROOT/code/ai_models"
INFRA_DIR="$PROJECT_ROOT/infrastructure"

# Required versions
REQUIRED_NODE_VERSION="18.0.0"
REQUIRED_PYTHON_VERSION="3.8.0"
REQUIRED_NPM_VERSION="8.0.0"
REQUIRED_YARN_VERSION="1.22.0"

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
    echo "[$level] $message" >> "$LOG_FILE"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to compare versions
version_greater_equal() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Function to check system type
get_system_type() {
    case "$(uname -s)" in
        Linux*)     echo "Linux";;
        Darwin*)    echo "macOS";;
        CYGWIN*)    echo "Windows";;
        MINGW*)     echo "Windows";;
        MSYS*)      echo "Windows";;
        *)          echo "Unknown";;
    esac
}

# Function to check if running in WSL
is_wsl() {
    if [ -f /proc/version ]; then
        if grep -q Microsoft /proc/version; then
            return 0
        fi
    fi
    return 1
}

# Function to install system dependencies based on OS
install_system_dependencies() {
    local system_type=$(get_system_type)

    log "STEP" "Installing system dependencies for $system_type..."

    case $system_type in
        "Linux")
            if command_exists apt-get; then
                log "INFO" "Updating package lists..."
                sudo apt-get update -y

                log "INFO" "Installing essential packages..."
                sudo apt-get install -y build-essential curl git python3 python3-pip python3-venv
            elif command_exists yum; then
                log "INFO" "Updating package lists..."
                sudo yum update -y

                log "INFO" "Installing essential packages..."
                sudo yum groupinstall -y "Development Tools"
                sudo yum install -y curl git python3 python3-pip
            else
                log "WARNING" "Unsupported Linux distribution. Please install dependencies manually."
            fi
            ;;
        "macOS")
            if ! command_exists brew; then
                log "INFO" "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi

            log "INFO" "Installing essential packages..."
            brew install git python@3 node
            ;;
        "Windows")
            if is_wsl; then
                log "INFO" "Running in WSL, installing Linux dependencies..."
                sudo apt-get update -y
                sudo apt-get install -y build-essential curl git python3 python3-pip python3-venv
            else
                log "WARNING" "Windows detected but not running in WSL. Please install dependencies manually."
            fi
            ;;
        *)
            log "WARNING" "Unsupported operating system. Please install dependencies manually."
            ;;
    esac
}

# Function to check and install Node.js
setup_node() {
    log "STEP" "Setting up Node.js environment..."

    if ! command_exists node; then
        log "INFO" "Node.js not found. Installing..."

        local system_type=$(get_system_type)
        case $system_type in
            "Linux")
                curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                sudo apt-get install -y nodejs
                ;;
            "macOS")
                brew install node@18
                ;;
            *)
                log "WARNING" "Please install Node.js manually for your system."
                return 1
                ;;
        esac
    else
        local node_version=$(node -v | cut -d 'v' -f 2)
        if ! version_greater_equal "$node_version" "$REQUIRED_NODE_VERSION"; then
            log "WARNING" "Node.js version $node_version is older than required version $REQUIRED_NODE_VERSION"
            log "INFO" "Please update Node.js to version $REQUIRED_NODE_VERSION or later"
        else
            log "INFO" "Node.js version $node_version is installed and meets requirements"
        fi
    fi

    # Check npm
    if ! command_exists npm; then
        log "ERROR" "npm not found. It should be installed with Node.js."
        return 1
    else
        local npm_version=$(npm -v)
        if ! version_greater_equal "$npm_version" "$REQUIRED_NPM_VERSION"; then
            log "WARNING" "npm version $npm_version is older than required version $REQUIRED_NPM_VERSION"
            log "INFO" "Updating npm..."
            sudo npm install -g npm@latest
        else
            log "INFO" "npm version $npm_version is installed and meets requirements"
        fi
    fi

    # Install Yarn if needed
    if ! command_exists yarn; then
        log "INFO" "Installing Yarn package manager..."
        sudo npm install -g yarn
    else
        local yarn_version=$(yarn -v)
        if ! version_greater_equal "$yarn_version" "$REQUIRED_YARN_VERSION"; then
            log "WARNING" "Yarn version $yarn_version is older than required version $REQUIRED_YARN_VERSION"
            log "INFO" "Updating Yarn..."
            sudo npm install -g yarn
        else
            log "INFO" "Yarn version $yarn_version is installed and meets requirements"
        fi
    fi

    # Install global npm packages
    log "INFO" "Installing required global npm packages..."
    sudo npm install -g truffle eslint prettier solhint expo-cli

    return 0
}

# Function to check and install Python
setup_python() {
    log "STEP" "Setting up Python environment..."

    if ! command_exists python3; then
        log "ERROR" "Python 3 not found. Please install Python 3.8 or later."
        return 1
    else
        local python_version=$(python3 --version | cut -d ' ' -f 2)
        if ! version_greater_equal "$python_version" "$REQUIRED_PYTHON_VERSION"; then
            log "WARNING" "Python version $python_version is older than required version $REQUIRED_PYTHON_VERSION"
            log "INFO" "Please update Python to version $REQUIRED_PYTHON_VERSION or later"
        else
            log "INFO" "Python version $python_version is installed and meets requirements"
        fi
    fi

    # Check pip
    if ! command_exists pip3; then
        log "ERROR" "pip3 not found. Please install pip for Python 3."
        return 1
    fi

    # Install Python virtual environment
    if ! command_exists python3 -m venv; then
        log "INFO" "Installing Python venv module..."

        local system_type=$(get_system_type)
        case $system_type in
            "Linux")
                if command_exists apt-get; then
                    sudo apt-get install -y python3-venv
                elif command_exists yum; then
                    sudo yum install -y python3-venv
                fi
                ;;
            *)
                log "WARNING" "Please install Python venv module manually for your system."
                ;;
        esac
    fi

    # Create virtual environment if it doesn't exist
    if [ ! -d "$PROJECT_ROOT/venv" ]; then
        log "INFO" "Creating Python virtual environment..."
        python3 -m venv "$PROJECT_ROOT/venv"
    fi

    # Install Python linting tools
    log "INFO" "Installing Python linting tools..."
    pip3 install --user black isort flake8 pylint

    return 0
}

# Function to set up backend
setup_backend() {
    log "STEP" "Setting up backend environment..."

    if [ ! -d "$BACKEND_DIR" ]; then
        log "ERROR" "Backend directory not found at $BACKEND_DIR"
        return 1
    fi

    log "INFO" "Installing backend dependencies..."
    cd "$BACKEND_DIR"

    # Activate virtual environment
    source "$PROJECT_ROOT/venv/bin/activate"

    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        log "WARNING" "requirements.txt not found in backend directory"
    fi

    # Deactivate virtual environment
    deactivate

    log "INFO" "Backend setup completed successfully"
    return 0
}

# Function to set up blockchain
setup_blockchain() {
    log "STEP" "Setting up blockchain environment..."

    if [ ! -d "$BLOCKCHAIN_DIR" ]; then
        log "ERROR" "Blockchain directory not found at $BLOCKCHAIN_DIR"
        return 1
    fi

    log "INFO" "Installing blockchain dependencies..."
    cd "$BLOCKCHAIN_DIR"

    # Install npm dependencies
    if [ -f "package.json" ]; then
        npm install
    else
        log "WARNING" "package.json not found in blockchain directory"
    fi

    log "INFO" "Blockchain setup completed successfully"
    return 0
}

# Function to set up web frontend
setup_web_frontend() {
    log "STEP" "Setting up web frontend environment..."

    if [ ! -d "$WEB_FRONTEND_DIR" ]; then
        log "ERROR" "Web frontend directory not found at $WEB_FRONTEND_DIR"
        return 1
    fi

    log "INFO" "Installing web frontend dependencies..."
    cd "$WEB_FRONTEND_DIR"

    # Install npm dependencies
    if [ -f "package.json" ]; then
        npm install
    else
        log "WARNING" "package.json not found in web frontend directory"
    fi

    log "INFO" "Web frontend setup completed successfully"
    return 0
}

# Function to set up mobile frontend
setup_mobile_frontend() {
    log "STEP" "Setting up mobile frontend environment..."

    if [ ! -d "$MOBILE_FRONTEND_DIR" ]; then
        log "ERROR" "Mobile frontend directory not found at $MOBILE_FRONTEND_DIR"
        return 1
    fi

    log "INFO" "Installing mobile frontend dependencies..."
    cd "$MOBILE_FRONTEND_DIR"

    # Install yarn dependencies
    if [ -f "package.json" ]; then
        yarn install
    else
        log "WARNING" "package.json not found in mobile frontend directory"
    fi

    log "INFO" "Mobile frontend setup completed successfully"
    return 0
}

# Function to validate the entire environment
validate_environment() {
    log "STEP" "Validating development environment..."

    local errors=0

    # Check required commands
    for cmd in node npm python3 pip3 git; do
        if ! command_exists "$cmd"; then
            log "ERROR" "Required command '$cmd' not found"
            errors=$((errors+1))
        fi
    done

    # Check optional but recommended commands
    for cmd in yarn truffle expo; do
        if ! command_exists "$cmd"; then
            log "WARNING" "Recommended command '$cmd' not found"
        fi
    done

    # Check project directories
    for dir in "$BACKEND_DIR" "$BLOCKCHAIN_DIR" "$WEB_FRONTEND_DIR"; do
        if [ ! -d "$dir" ]; then
            log "ERROR" "Required directory '$dir' not found"
            errors=$((errors+1))
        fi
    done

    # Check optional directories
    for dir in "$MOBILE_FRONTEND_DIR" "$AI_MODELS_DIR" "$INFRA_DIR"; do
        if [ ! -d "$dir" ]; then
            log "WARNING" "Optional directory '$dir' not found"
        fi
    done

    # Check virtual environment
    if [ ! -d "$PROJECT_ROOT/venv" ]; then
        log "ERROR" "Python virtual environment not found at $PROJECT_ROOT/venv"
        errors=$((errors+1))
    fi

    if [ $errors -eq 0 ]; then
        log "INFO" "Environment validation completed successfully"
        return 0
    else
        log "ERROR" "Environment validation failed with $errors errors"
        return 1
    fi
}

# Function to check for outdated dependencies
check_outdated_dependencies() {
    log "STEP" "Checking for outdated dependencies..."

    # Check backend dependencies
    if [ -d "$BACKEND_DIR" ]; then
        log "INFO" "Checking backend dependencies..."
        cd "$BACKEND_DIR"
        source "$PROJECT_ROOT/venv/bin/activate"
        pip list --outdated
        deactivate
    fi

    # Check web frontend dependencies
    if [ -d "$WEB_FRONTEND_DIR" ]; then
        log "INFO" "Checking web frontend dependencies..."
        cd "$WEB_FRONTEND_DIR"
        npm outdated
    fi

    # Check blockchain dependencies
    if [ -d "$BLOCKCHAIN_DIR" ]; then
        log "INFO" "Checking blockchain dependencies..."
        cd "$BLOCKCHAIN_DIR"
        npm outdated
    fi

    # Check mobile frontend dependencies
    if [ -d "$MOBILE_FRONTEND_DIR" ]; then
        log "INFO" "Checking mobile frontend dependencies..."
        cd "$MOBILE_FRONTEND_DIR"
        yarn outdated
    fi

    log "INFO" "Dependency check completed"
}

# Function to display help message
show_help() {
    echo "CarbonXchange Environment Manager"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --help, -h                 Show this help message"
    echo "  --all                      Set up and validate the entire environment"
    echo "  --system                   Install system dependencies"
    echo "  --node                     Set up Node.js environment"
    echo "  --python                   Set up Python environment"
    echo "  --backend                  Set up backend environment"
    echo "  --blockchain               Set up blockchain environment"
    echo "  --web-frontend             Set up web frontend environment"
    echo "  --mobile-frontend          Set up mobile frontend environment"
    echo "  --validate                 Validate the environment"
    echo "  --check-outdated           Check for outdated dependencies"
    echo ""
    echo "Examples:"
    echo "  $0 --all                   Set up everything"
    echo "  $0 --validate              Only validate the environment"
    echo "  $0 --backend --web-frontend  Set up backend and web frontend only"
}

# Main function
main() {
    # Initialize log file
    echo "CarbonXchange Environment Manager Log - $(date)" > "$LOG_FILE"

    # Parse command line arguments
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    local setup_all=false
    local setup_system=false
    local setup_node_env=false
    local setup_python_env=false
    local setup_backend_env=false
    local setup_blockchain_env=false
    local setup_web_frontend_env=false
    local setup_mobile_frontend_env=false
    local validate_env=false
    local check_outdated=false

    while [ $# -gt 0 ]; do
        case "$1" in
            --help|-h)
                show_help
                exit 0
                ;;
            --all)
                setup_all=true
                ;;
            --system)
                setup_system=true
                ;;
            --node)
                setup_node_env=true
                ;;
            --python)
                setup_python_env=true
                ;;
            --backend)
                setup_backend_env=true
                ;;
            --blockchain)
                setup_blockchain_env=true
                ;;
            --web-frontend)
                setup_web_frontend_env=true
                ;;
            --mobile-frontend)
                setup_mobile_frontend_env=true
                ;;
            --validate)
                validate_env=true
                ;;
            --check-outdated)
                check_outdated=true
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done

    # If --all is specified, set all options to true
    if [ "$setup_all" = true ]; then
        setup_system=true
        setup_node_env=true
        setup_python_env=true
        setup_backend_env=true
        setup_blockchain_env=true
        setup_web_frontend_env=true
        setup_mobile_frontend_env=true
        validate_env=true
    fi

    # Print banner
    echo "========================================================"
    echo "  CarbonXchange Environment Manager"
    echo "========================================================"
    echo ""

    # Execute requested actions
    if [ "$setup_system" = true ]; then
        install_system_dependencies
    fi

    if [ "$setup_node_env" = true ]; then
        setup_node
    fi

    if [ "$setup_python_env" = true ]; then
        setup_python
    fi

    if [ "$setup_backend_env" = true ]; then
        setup_backend
    fi

    if [ "$setup_blockchain_env" = true ]; then
        setup_blockchain
    fi

    if [ "$setup_web_frontend_env" = true ]; then
        setup_web_frontend
    fi

    if [ "$setup_mobile_frontend_env" = true ]; then
        setup_mobile_frontend
    fi

    if [ "$validate_env" = true ]; then
        validate_environment
    fi

    if [ "$check_outdated" = true ]; then
        check_outdated_dependencies
    fi

    log "INFO" "Environment manager completed all requested tasks"
    echo ""
    echo "Log file: $LOG_FILE"
    echo ""
}

# Run main function
main "$@"
