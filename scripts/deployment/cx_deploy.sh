#!/bin/bash
# CarbonXchange Deployment Pipeline Enhancer
# A script to automate deployment processes for different environments
#
# Features:
# - Environment-specific deployment (dev, staging, production)
# - Configuration management
# - Deployment validation
# - Rollback automation

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
INFRA_DIR="$PROJECT_ROOT/infrastructure"

# Deployment directories
DEPLOY_DIR="$PROJECT_ROOT/deploy"
mkdir -p "$DEPLOY_DIR"

# Backup directory for rollbacks
BACKUP_DIR="$PROJECT_ROOT/deploy/backups"
mkdir -p "$BACKUP_DIR"

# Environment configuration templates
ENV_TEMPLATES_DIR="$PROJECT_ROOT/infrastructure/env-templates"

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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate environment name
validate_environment() {
    local env=$1

    case $env in
        "dev"|"development")
            echo "dev"
            ;;
        "staging"|"test")
            echo "staging"
            ;;
        "prod"|"production")
            echo "prod"
            ;;
        *)
            log "ERROR" "Invalid environment: $env. Must be one of: dev, staging, prod"
            return 1
            ;;
    esac
}

# Function to generate environment-specific configuration
generate_config() {
    local env=$1

    log "STEP" "Generating configuration for $env environment..."

    if [ ! -d "$ENV_TEMPLATES_DIR" ]; then
        log "ERROR" "Environment templates directory not found at $ENV_TEMPLATES_DIR"
        return 1
    fi

    # Create environment-specific config directory
    local config_dir="$DEPLOY_DIR/$env/config"
    mkdir -p "$config_dir"

    # Process each template file
    for template in "$ENV_TEMPLATES_DIR"/*.template; do
        if [ -f "$template" ]; then
            local filename=$(basename "$template" .template)
            log "INFO" "Processing template: $filename"

            # Replace environment variables in template
            envsubst < "$template" > "$config_dir/$filename"

            log "INFO" "Generated $filename for $env environment"
        fi
    done

    # Generate .env file for backend
    if [ -f "$ENV_TEMPLATES_DIR/.env.$env" ]; then
        log "INFO" "Copying .env file for backend..."
        cp "$ENV_TEMPLATES_DIR/.env.$env" "$config_dir/.env"
    else
        log "WARNING" ".env.$env file not found in templates directory"
    fi

    log "INFO" "Configuration generation completed for $env environment"
    return 0
}

# Function to build backend for deployment
build_backend() {
    local env=$1

    log "STEP" "Building backend for $env environment..."

    if [ ! -d "$BACKEND_DIR" ]; then
        log "ERROR" "Backend directory not found at $BACKEND_DIR"
        return 1
    fi

    # Create deployment directory
    local deploy_backend_dir="$DEPLOY_DIR/$env/backend"
    mkdir -p "$deploy_backend_dir"

    # Copy backend code
    log "INFO" "Copying backend code..."
    rsync -av --exclude="__pycache__" --exclude="*.pyc" --exclude=".pytest_cache" \
        "$BACKEND_DIR/" "$deploy_backend_dir/"

    # Copy environment-specific configuration
    log "INFO" "Copying environment configuration..."
    cp "$DEPLOY_DIR/$env/config/.env" "$deploy_backend_dir/"

    # Install dependencies in a virtual environment
    log "INFO" "Setting up virtual environment..."
    cd "$deploy_backend_dir"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

    # Run database migrations if needed
    if [ -f "manage.py" ]; then
        log "INFO" "Running database migrations..."
        python manage.py migrate
    fi

    # Deactivate virtual environment
    deactivate

    log "INFO" "Backend build completed for $env environment"
    return 0
}

# Function to build web frontend for deployment
build_web_frontend() {
    local env=$1

    log "STEP" "Building web frontend for $env environment..."

    if [ ! -d "$WEB_FRONTEND_DIR" ]; then
        log "ERROR" "Web frontend directory not found at $WEB_FRONTEND_DIR"
        return 1
    fi

    # Create deployment directory
    local deploy_frontend_dir="$DEPLOY_DIR/$env/web-frontend"
    mkdir -p "$deploy_frontend_dir"

    # Copy frontend code
    log "INFO" "Copying web frontend code..."
    rsync -av --exclude="node_modules" --exclude="build" --exclude=".cache" \
        "$WEB_FRONTEND_DIR/" "$deploy_frontend_dir/"

    # Copy environment-specific configuration
    log "INFO" "Setting up environment configuration..."
    cp "$DEPLOY_DIR/$env/config/frontend.env.js" "$deploy_frontend_dir/.env"

    # Install dependencies and build
    log "INFO" "Installing dependencies and building web frontend..."
    cd "$deploy_frontend_dir"
    npm install
    npm run build

    log "INFO" "Web frontend build completed for $env environment"
    return 0
}

# Function to build blockchain contracts for deployment
build_blockchain() {
    local env=$1

    log "STEP" "Building blockchain contracts for $env environment..."

    if [ ! -d "$BLOCKCHAIN_DIR" ]; then
        log "ERROR" "Blockchain directory not found at $BLOCKCHAIN_DIR"
        return 1
    fi

    # Create deployment directory
    local deploy_blockchain_dir="$DEPLOY_DIR/$env/blockchain"
    mkdir -p "$deploy_blockchain_dir"

    # Copy blockchain code
    log "INFO" "Copying blockchain code..."
    rsync -av --exclude="node_modules" --exclude="build" \
        "$BLOCKCHAIN_DIR/" "$deploy_blockchain_dir/"

    # Copy environment-specific configuration
    log "INFO" "Setting up environment configuration..."
    cp "$DEPLOY_DIR/$env/config/truffle-config.js" "$deploy_blockchain_dir/truffle-config.js"

    # Install dependencies and compile contracts
    log "INFO" "Installing dependencies and compiling contracts..."
    cd "$deploy_blockchain_dir"
    npm install
    npx truffle compile

    log "INFO" "Blockchain contracts build completed for $env environment"
    return 0
}

# Function to deploy to environment
deploy_to_environment() {
    local env=$1

    log "STEP" "Deploying to $env environment..."

    # Validate that builds exist
    if [ ! -d "$DEPLOY_DIR/$env" ]; then
        log "ERROR" "Build directory for $env not found. Run build first."
        return 1
    fi

    # Create backup for rollback
    create_backup "$env"

    # Deploy backend
    if [ -d "$DEPLOY_DIR/$env/backend" ]; then
        log "INFO" "Deploying backend..."

        case $env in
            "dev")
                # For dev, we might just use the local build
                log "INFO" "Using local backend build for dev environment"
                ;;
            "staging")
                # For staging, deploy to test server
                log "INFO" "Deploying backend to staging server..."
                # Example: rsync to staging server
                # rsync -avz --delete "$DEPLOY_DIR/$env/backend/" "user@staging-server:/path/to/backend/"
                ;;
            "prod")
                # For production, deploy to production server
                log "INFO" "Deploying backend to production server..."
                # Example: rsync to production server
                # rsync -avz --delete "$DEPLOY_DIR/$env/backend/" "user@production-server:/path/to/backend/"
                ;;
        esac
    fi

    # Deploy web frontend
    if [ -d "$DEPLOY_DIR/$env/web-frontend/build" ]; then
        log "INFO" "Deploying web frontend..."

        case $env in
            "dev")
                # For dev, we might just use the local build
                log "INFO" "Using local web frontend build for dev environment"
                ;;
            "staging")
                # For staging, deploy to test server
                log "INFO" "Deploying web frontend to staging server..."
                # Example: rsync to staging server
                # rsync -avz --delete "$DEPLOY_DIR/$env/web-frontend/build/" "user@staging-server:/path/to/web-frontend/"
                ;;
            "prod")
                # For production, deploy to production server
                log "INFO" "Deploying web frontend to production server..."
                # Example: rsync to production server
                # rsync -avz --delete "$DEPLOY_DIR/$env/web-frontend/build/" "user@production-server:/path/to/web-frontend/"
                ;;
        esac
    fi

    # Deploy blockchain contracts
    if [ -d "$DEPLOY_DIR/$env/blockchain" ]; then
        log "INFO" "Deploying blockchain contracts..."

        case $env in
            "dev")
                # For dev, deploy to local blockchain
                log "INFO" "Deploying contracts to local blockchain..."
                cd "$DEPLOY_DIR/$env/blockchain"
                npx truffle migrate --network development
                ;;
            "staging")
                # For staging, deploy to test network
                log "INFO" "Deploying contracts to test network..."
                cd "$DEPLOY_DIR/$env/blockchain"
                npx truffle migrate --network testnet
                ;;
            "prod")
                # For production, deploy to mainnet
                log "INFO" "Deploying contracts to mainnet..."
                cd "$DEPLOY_DIR/$env/blockchain"
                npx truffle migrate --network mainnet
                ;;
        esac
    fi

    log "INFO" "Deployment to $env environment completed"

    # Validate deployment
    validate_deployment "$env"

    return 0
}

# Function to create backup for rollback
create_backup() {
    local env=$1
    local timestamp=$(date +"%Y%m%d%H%M%S")

    log "STEP" "Creating backup for $env environment..."

    # Create backup directory
    local backup_dir="$BACKUP_DIR/${env}_${timestamp}"
    mkdir -p "$backup_dir"

    # Backup backend
    if [ -d "$DEPLOY_DIR/$env/backend" ]; then
        log "INFO" "Backing up backend..."
        mkdir -p "$backup_dir/backend"
        rsync -av "$DEPLOY_DIR/$env/backend/" "$backup_dir/backend/"
    fi

    # Backup web frontend
    if [ -d "$DEPLOY_DIR/$env/web-frontend" ]; then
        log "INFO" "Backing up web frontend..."
        mkdir -p "$backup_dir/web-frontend"
        rsync -av "$DEPLOY_DIR/$env/web-frontend/build/" "$backup_dir/web-frontend/"
    fi

    # Backup blockchain contracts
    if [ -d "$DEPLOY_DIR/$env/blockchain" ]; then
        log "INFO" "Backing up blockchain contracts..."
        mkdir -p "$backup_dir/blockchain"
        rsync -av "$DEPLOY_DIR/$env/blockchain/build/" "$backup_dir/blockchain/"
    fi

    # Save backup info
    echo "$timestamp" > "$DEPLOY_DIR/$env/last_backup"

    log "INFO" "Backup created at $backup_dir"
    return 0
}

# Function to validate deployment
validate_deployment() {
    local env=$1

    log "STEP" "Validating deployment for $env environment..."

    # Define endpoints to check based on environment
    local backend_url=""
    local frontend_url=""

    case $env in
        "dev")
            backend_url="http://localhost:5000/api/health"
            frontend_url="http://localhost:3000"
            ;;
        "staging")
            backend_url="https://api.staging.carbonxchange.com/api/health"
            frontend_url="https://staging.carbonxchange.com"
            ;;
        "prod")
            backend_url="https://api.carbonxchange.com/api/health"
            frontend_url="https://carbonxchange.com"
            ;;
    esac

    # Check backend health
    if [ -n "$backend_url" ]; then
        log "INFO" "Checking backend health at $backend_url..."
        if curl -s "$backend_url" | grep -q "healthy"; then
            log "INFO" "Backend is healthy"
        else
            log "ERROR" "Backend health check failed"
            return 1
        fi
    fi

    # Check frontend
    if [ -n "$frontend_url" ]; then
        log "INFO" "Checking frontend at $frontend_url..."
        if curl -s -I "$frontend_url" | grep -q "200 OK"; then
            log "INFO" "Frontend is accessible"
        else
            log "ERROR" "Frontend check failed"
            return 1
        fi
    fi

    log "INFO" "Deployment validation completed successfully"
    return 0
}

# Function to rollback deployment
rollback_deployment() {
    local env=$1

    log "STEP" "Rolling back deployment for $env environment..."

    # Check if last backup exists
    if [ ! -f "$DEPLOY_DIR/$env/last_backup" ]; then
        log "ERROR" "No backup found for $env environment"
        return 1
    fi

    local timestamp=$(cat "$DEPLOY_DIR/$env/last_backup")
    local backup_dir="$BACKUP_DIR/${env}_${timestamp}"

    if [ ! -d "$backup_dir" ]; then
        log "ERROR" "Backup directory not found: $backup_dir"
        return 1
    fi

    # Rollback backend
    if [ -d "$backup_dir/backend" ]; then
        log "INFO" "Rolling back backend..."

        case $env in
            "dev")
                # For dev, we might just restore the local backup
                log "INFO" "Restoring local backend backup for dev environment"
                rsync -av --delete "$backup_dir/backend/" "$DEPLOY_DIR/$env/backend/"
                ;;
            "staging")
                # For staging, restore to test server
                log "INFO" "Rolling back backend on staging server..."
                # Example: rsync to staging server
                # rsync -avz --delete "$backup_dir/backend/" "user@staging-server:/path/to/backend/"
                ;;
            "prod")
                # For production, restore to production server
                log "INFO" "Rolling back backend on production server..."
                # Example: rsync to production server
                # rsync -avz --delete "$backup_dir/backend/" "user@production-server:/path/to/backend/"
                ;;
        esac
    fi

    # Rollback web frontend
    if [ -d "$backup_dir/web-frontend" ]; then
        log "INFO" "Rolling back web frontend..."

        case $env in
            "dev")
                # For dev, we might just restore the local backup
                log "INFO" "Restoring local web frontend backup for dev environment"
                rsync -av --delete "$backup_dir/web-frontend/" "$DEPLOY_DIR/$env/web-frontend/build/"
                ;;
            "staging")
                # For staging, restore to test server
                log "INFO" "Rolling back web frontend on staging server..."
                # Example: rsync to staging server
                # rsync -avz --delete "$backup_dir/web-frontend/" "user@staging-server:/path/to/web-frontend/"
                ;;
            "prod")
                # For production, restore to production server
                log "INFO" "Rolling back web frontend on production server..."
                # Example: rsync to production server
                # rsync -avz --delete "$backup_dir/web-frontend/" "user@production-server:/path/to/web-frontend/"
                ;;
        esac
    fi

    # Note: Blockchain contracts typically can't be rolled back once deployed
    # We can only deploy a new version with fixes

    log "INFO" "Rollback completed for $env environment"

    # Validate rollback
    validate_deployment "$env"

    return 0
}

# Function to display help message
show_help() {
    echo "CarbonXchange Deployment Pipeline Enhancer"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  config <environment>        Generate configuration for environment"
    echo "  build <environment>         Build all components for environment"
    echo "  deploy <environment>        Deploy to environment"
    echo "  validate <environment>      Validate deployment in environment"
    echo "  rollback <environment>      Rollback to previous deployment"
    echo "  help                        Show this help message"
    echo ""
    echo "Environments:"
    echo "  dev, development            Development environment"
    echo "  staging, test               Staging/testing environment"
    echo "  prod, production            Production environment"
    echo ""
    echo "Options:"
    echo "  --backend-only              Only perform action on backend"
    echo "  --frontend-only             Only perform action on web frontend"
    echo "  --blockchain-only           Only perform action on blockchain contracts"
    echo ""
    echo "Examples:"
    echo "  $0 config dev               Generate configuration for development environment"
    echo "  $0 build staging            Build all components for staging environment"
    echo "  $0 deploy prod              Deploy to production environment"
    echo "  $0 rollback prod            Rollback production to previous deployment"
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
        "config")
            if [ $# -eq 0 ]; then
                log "ERROR" "Environment required for config command"
                exit 1
            fi

            local env=$(validate_environment "$1")
            if [ $? -ne 0 ]; then
                exit 1
            fi

            generate_config "$env"
            ;;
        "build")
            if [ $# -eq 0 ]; then
                log "ERROR" "Environment required for build command"
                exit 1
            fi

            local env=$(validate_environment "$1")
            if [ $? -ne 0 ]; then
                exit 1
            fi

            shift

            # Parse options
            local backend_only=false
            local frontend_only=false
            local blockchain_only=false

            while [ $# -gt 0 ]; do
                case "$1" in
                    --backend-only)
                        backend_only=true
                        ;;
                    --frontend-only)
                        frontend_only=true
                        ;;
                    --blockchain-only)
                        blockchain_only=true
                        ;;
                    *)
                        log "ERROR" "Unknown option: $1"
                        show_help
                        exit 1
                        ;;
                esac
                shift
            done

            # Generate config first
            generate_config "$env"

            # Build components based on options
            if [ "$backend_only" = true ]; then
                build_backend "$env"
            elif [ "$frontend_only" = true ]; then
                build_web_frontend "$env"
            elif [ "$blockchain_only" = true ]; then
                build_blockchain "$env"
            else
                # Build all components
                build_backend "$env"
                build_web_frontend "$env"
                build_blockchain "$env"
            fi
            ;;
        "deploy")
            if [ $# -eq 0 ]; then
                log "ERROR" "Environment required for deploy command"
                exit 1
            fi

            local env=$(validate_environment "$1")
            if [ $? -ne 0 ]; then
                exit 1
            fi

            deploy_to_environment "$env"
            ;;
        "validate")
            if [ $# -eq 0 ]; then
                log "ERROR" "Environment required for validate command"
                exit 1
            fi

            local env=$(validate_environment "$1")
            if [ $? -ne 0 ]; then
                exit 1
            fi

            validate_deployment "$env"
            ;;
        "rollback")
            if [ $# -eq 0 ]; then
                log "ERROR" "Environment required for rollback command"
                exit 1
            fi

            local env=$(validate_environment "$1")
            if [ $? -ne 0 ]; then
                exit 1
            fi

            rollback_deployment "$env"
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

# Run main function
main "$@"
