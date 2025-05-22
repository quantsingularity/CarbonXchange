#!/bin/bash
# CarbonXchange Test Automation Suite
# A comprehensive script to automate all testing processes
#
# Features:
# - Run unit tests for all components
# - Run integration tests
# - Run end-to-end tests
# - Generate test reports
# - Set up pre-commit hooks for testing

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
AI_MODELS_DIR="$PROJECT_ROOT/code/ai_models"

# Report directory
REPORT_DIR="$PROJECT_ROOT/test-reports"
mkdir -p "$REPORT_DIR"

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

# Function to run backend tests
run_backend_tests() {
    local test_type=$1  # unit, integration, or all
    
    log "STEP" "Running backend $test_type tests..."
    
    if [ ! -d "$BACKEND_DIR" ]; then
        log "ERROR" "Backend directory not found at $BACKEND_DIR"
        return 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Activate virtual environment
    source "$PROJECT_ROOT/venv/bin/activate"
    
    # Create test report directory
    local report_dir="$REPORT_DIR/backend"
    mkdir -p "$report_dir"
    
    # Run tests based on type
    case $test_type in
        "unit")
            log "INFO" "Running backend unit tests..."
            python -m pytest tests/unit --junitxml="$report_dir/unit-tests.xml" -v
            ;;
        "integration")
            log "INFO" "Running backend integration tests..."
            python -m pytest tests/integration --junitxml="$report_dir/integration-tests.xml" -v
            ;;
        "all")
            log "INFO" "Running all backend tests..."
            python -m pytest tests --junitxml="$report_dir/all-tests.xml" -v
            ;;
        *)
            log "ERROR" "Unknown test type: $test_type"
            return 1
            ;;
    esac
    
    local exit_code=$?
    
    # Deactivate virtual environment
    deactivate
    
    if [ $exit_code -eq 0 ]; then
        log "INFO" "Backend $test_type tests completed successfully"
    else
        log "ERROR" "Backend $test_type tests failed with exit code $exit_code"
        return $exit_code
    fi
    
    return 0
}

# Function to run blockchain tests
run_blockchain_tests() {
    log "STEP" "Running blockchain tests..."
    
    if [ ! -d "$BLOCKCHAIN_DIR" ]; then
        log "ERROR" "Blockchain directory not found at $BLOCKCHAIN_DIR"
        return 1
    fi
    
    cd "$BLOCKCHAIN_DIR"
    
    # Create test report directory
    local report_dir="$REPORT_DIR/blockchain"
    mkdir -p "$report_dir"
    
    # Run tests
    log "INFO" "Running blockchain tests with Truffle..."
    npx truffle test --reporter mocha-junit-reporter --reporter-options mochaFile="$report_dir/blockchain-tests.xml"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log "INFO" "Blockchain tests completed successfully"
    else
        log "ERROR" "Blockchain tests failed with exit code $exit_code"
        return $exit_code
    fi
    
    return 0
}

# Function to run web frontend tests
run_web_frontend_tests() {
    local test_type=$1  # unit, integration, or all
    
    log "STEP" "Running web frontend $test_type tests..."
    
    if [ ! -d "$WEB_FRONTEND_DIR" ]; then
        log "ERROR" "Web frontend directory not found at $WEB_FRONTEND_DIR"
        return 1
    fi
    
    cd "$WEB_FRONTEND_DIR"
    
    # Create test report directory
    local report_dir="$REPORT_DIR/web-frontend"
    mkdir -p "$report_dir"
    
    # Run tests based on type
    case $test_type in
        "unit")
            log "INFO" "Running web frontend unit tests..."
            npm test -- --testPathPattern=src/.*\\.test\\.(js|jsx|ts|tsx)$ --json --outputFile="$report_dir/unit-tests.json"
            ;;
        "integration")
            log "INFO" "Running web frontend integration tests..."
            npm test -- --testPathPattern=src/.*\\.integration\\.(js|jsx|ts|tsx)$ --json --outputFile="$report_dir/integration-tests.json"
            ;;
        "all")
            log "INFO" "Running all web frontend tests..."
            npm test -- --json --outputFile="$report_dir/all-tests.json"
            ;;
        *)
            log "ERROR" "Unknown test type: $test_type"
            return 1
            ;;
    esac
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log "INFO" "Web frontend $test_type tests completed successfully"
    else
        log "ERROR" "Web frontend $test_type tests failed with exit code $exit_code"
        return $exit_code
    fi
    
    return 0
}

# Function to run mobile frontend tests
run_mobile_frontend_tests() {
    log "STEP" "Running mobile frontend tests..."
    
    if [ ! -d "$MOBILE_FRONTEND_DIR" ]; then
        log "ERROR" "Mobile frontend directory not found at $MOBILE_FRONTEND_DIR"
        return 1
    fi
    
    cd "$MOBILE_FRONTEND_DIR"
    
    # Create test report directory
    local report_dir="$REPORT_DIR/mobile-frontend"
    mkdir -p "$report_dir"
    
    # Run tests
    log "INFO" "Running mobile frontend tests..."
    yarn test --json --outputFile="$report_dir/mobile-tests.json"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log "INFO" "Mobile frontend tests completed successfully"
    else
        log "ERROR" "Mobile frontend tests failed with exit code $exit_code"
        return $exit_code
    fi
    
    return 0
}

# Function to run AI model tests
run_ai_model_tests() {
    log "STEP" "Running AI model tests..."
    
    if [ ! -d "$AI_MODELS_DIR" ]; then
        log "ERROR" "AI models directory not found at $AI_MODELS_DIR"
        return 1
    fi
    
    cd "$AI_MODELS_DIR"
    
    # Activate virtual environment
    source "$PROJECT_ROOT/venv/bin/activate"
    
    # Create test report directory
    local report_dir="$REPORT_DIR/ai-models"
    mkdir -p "$report_dir"
    
    # Run tests
    log "INFO" "Running AI model tests..."
    python -m pytest tests --junitxml="$report_dir/ai-model-tests.xml" -v
    
    local exit_code=$?
    
    # Deactivate virtual environment
    deactivate
    
    if [ $exit_code -eq 0 ]; then
        log "INFO" "AI model tests completed successfully"
    else
        log "ERROR" "AI model tests failed with exit code $exit_code"
        return $exit_code
    fi
    
    return 0
}

# Function to run end-to-end tests
run_e2e_tests() {
    log "STEP" "Running end-to-end tests..."
    
    # Create test report directory
    local report_dir="$REPORT_DIR/e2e"
    mkdir -p "$report_dir"
    
    # Check if Cypress is installed
    if ! command_exists npx cypress; then
        log "WARNING" "Cypress not found. Installing..."
        npm install -g cypress
    fi
    
    # Run Cypress tests
    log "INFO" "Running end-to-end tests with Cypress..."
    cd "$PROJECT_ROOT"
    npx cypress run --reporter junit --reporter-options "mochaFile=$report_dir/e2e-tests.xml"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log "INFO" "End-to-end tests completed successfully"
    else
        log "ERROR" "End-to-end tests failed with exit code $exit_code"
        return $exit_code
    fi
    
    return 0
}

# Function to generate test coverage report
generate_coverage_report() {
    log "STEP" "Generating test coverage reports..."
    
    # Create coverage report directory
    local coverage_dir="$REPORT_DIR/coverage"
    mkdir -p "$coverage_dir"
    
    # Backend coverage
    if [ -d "$BACKEND_DIR" ]; then
        log "INFO" "Generating backend coverage report..."
        cd "$BACKEND_DIR"
        source "$PROJECT_ROOT/venv/bin/activate"
        python -m pytest --cov=. --cov-report=xml:$coverage_dir/backend-coverage.xml tests/
        deactivate
    fi
    
    # Web frontend coverage
    if [ -d "$WEB_FRONTEND_DIR" ]; then
        log "INFO" "Generating web frontend coverage report..."
        cd "$WEB_FRONTEND_DIR"
        npm test -- --coverage --coverageDirectory="$coverage_dir/web-frontend"
    fi
    
    # Mobile frontend coverage
    if [ -d "$MOBILE_FRONTEND_DIR" ]; then
        log "INFO" "Generating mobile frontend coverage report..."
        cd "$MOBILE_FRONTEND_DIR"
        yarn test --coverage --coverageDirectory="$coverage_dir/mobile-frontend"
    fi
    
    log "INFO" "Coverage reports generated in $coverage_dir"
}

# Function to set up pre-commit hooks
setup_pre_commit_hooks() {
    log "STEP" "Setting up pre-commit hooks..."
    
    # Check if git is initialized
    if [ ! -d "$PROJECT_ROOT/.git" ]; then
        log "ERROR" "Git repository not found at $PROJECT_ROOT"
        return 1
    fi
    
    # Create hooks directory if it doesn't exist
    local hooks_dir="$PROJECT_ROOT/.git/hooks"
    mkdir -p "$hooks_dir"
    
    # Create pre-commit hook
    log "INFO" "Creating pre-commit hook..."
    cat > "$hooks_dir/pre-commit" << 'EOF'
#!/bin/bash

# CarbonXchange pre-commit hook
# This hook runs linting and unit tests before allowing a commit

echo "Running pre-commit checks..."

# Get the project root directory
PROJECT_ROOT=$(git rev-parse --show-toplevel)

# Run linting
echo "Running linting..."
$PROJECT_ROOT/lint-all.sh

if [ $? -ne 0 ]; then
    echo "Linting failed. Please fix the issues before committing."
    exit 1
fi

# Run unit tests
echo "Running unit tests..."
$PROJECT_ROOT/carbonxchange_automation/testing/cx_test_runner.sh --unit-only

if [ $? -ne 0 ]; then
    echo "Unit tests failed. Please fix the issues before committing."
    exit 1
fi

echo "Pre-commit checks passed!"
exit 0
EOF
    
    # Make the hook executable
    chmod +x "$hooks_dir/pre-commit"
    
    log "INFO" "Pre-commit hook set up successfully"
}

# Function to run unit tests only
run_unit_tests_only() {
    log "STEP" "Running unit tests for all components..."
    
    local exit_code=0
    
    # Run backend unit tests
    run_backend_tests "unit"
    if [ $? -ne 0 ]; then
        exit_code=1
    fi
    
    # Run web frontend unit tests
    run_web_frontend_tests "unit"
    if [ $? -ne 0 ]; then
        exit_code=1
    fi
    
    # Run blockchain tests (usually only unit tests)
    run_blockchain_tests
    if [ $? -ne 0 ]; then
        exit_code=1
    fi
    
    # Run mobile frontend tests (usually only unit tests)
    run_mobile_frontend_tests
    if [ $? -ne 0 ]; then
        exit_code=1
    fi
    
    return $exit_code
}

# Function to display help message
show_help() {
    echo "CarbonXchange Test Automation Suite"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --help, -h                 Show this help message"
    echo "  --all                      Run all tests (unit, integration, e2e)"
    echo "  --unit-only                Run only unit tests for all components"
    echo "  --integration-only         Run only integration tests for all components"
    echo "  --e2e-only                 Run only end-to-end tests"
    echo "  --backend                  Run all backend tests"
    echo "  --blockchain               Run all blockchain tests"
    echo "  --web-frontend             Run all web frontend tests"
    echo "  --mobile-frontend          Run all mobile frontend tests"
    echo "  --ai-models                Run all AI model tests"
    echo "  --coverage                 Generate test coverage reports"
    echo "  --setup-hooks              Set up git pre-commit hooks"
    echo ""
    echo "Examples:"
    echo "  $0 --all                   Run all tests"
    echo "  $0 --unit-only             Run only unit tests"
    echo "  $0 --backend --coverage    Run backend tests and generate coverage report"
}

# Main function
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    local run_all=false
    local run_unit_only=false
    local run_integration_only=false
    local run_e2e_only=false
    local run_backend=false
    local run_blockchain=false
    local run_web_frontend=false
    local run_mobile_frontend=false
    local run_ai_models=false
    local gen_coverage=false
    local setup_hooks=false
    
    # Parse command line arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --help|-h)
                show_help
                exit 0
                ;;
            --all)
                run_all=true
                ;;
            --unit-only)
                run_unit_only=true
                ;;
            --integration-only)
                run_integration_only=true
                ;;
            --e2e-only)
                run_e2e_only=true
                ;;
            --backend)
                run_backend=true
                ;;
            --blockchain)
                run_blockchain=true
                ;;
            --web-frontend)
                run_web_frontend=true
                ;;
            --mobile-frontend)
                run_mobile_frontend=true
                ;;
            --ai-models)
                run_ai_models=true
                ;;
            --coverage)
                gen_coverage=true
                ;;
            --setup-hooks)
                setup_hooks=true
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done
    
    # Print banner
    echo "========================================================"
    echo "  CarbonXchange Test Automation Suite"
    echo "========================================================"
    echo ""
    
    # Set up pre-commit hooks if requested
    if [ "$setup_hooks" = true ]; then
        setup_pre_commit_hooks
        exit $?
    fi
    
    # Run tests based on options
    if [ "$run_all" = true ]; then
        # Run all tests
        run_backend_tests "all"
        run_blockchain_tests
        run_web_frontend_tests "all"
        run_mobile_frontend_tests
        run_ai_model_tests
        run_e2e_tests
    elif [ "$run_unit_only" = true ]; then
        # Run only unit tests
        run_unit_tests_only
    elif [ "$run_integration_only" = true ]; then
        # Run only integration tests
        run_backend_tests "integration"
        run_web_frontend_tests "integration"
    elif [ "$run_e2e_only" = true ]; then
        # Run only end-to-end tests
        run_e2e_tests
    else
        # Run tests for specific components
        if [ "$run_backend" = true ]; then
            run_backend_tests "all"
        fi
        
        if [ "$run_blockchain" = true ]; then
            run_blockchain_tests
        fi
        
        if [ "$run_web_frontend" = true ]; then
            run_web_frontend_tests "all"
        fi
        
        if [ "$run_mobile_frontend" = true ]; then
            run_mobile_frontend_tests
        fi
        
        if [ "$run_ai_models" = true ]; then
            run_ai_model_tests
        fi
    fi
    
    # Generate coverage reports if requested
    if [ "$gen_coverage" = true ]; then
        generate_coverage_report
    fi
    
    log "INFO" "Test automation completed"
    echo ""
    log "INFO" "Test reports available in: $REPORT_DIR"
    echo ""
}

# Run main function
main "$@"
