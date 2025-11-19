#!/bin/bash
# CarbonXchange Documentation Generator
# A script to automate documentation generation and validation
#
# Features:
# - API documentation generation
# - Project status reporting
# - Changelog generation
# - Documentation validation

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
DOCS_DIR="$PROJECT_ROOT/docs"

# Output directory for generated documentation
OUTPUT_DIR="$PROJECT_ROOT/generated-docs"
mkdir -p "$OUTPUT_DIR"

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

# Function to generate API documentation
generate_api_docs() {
    log "STEP" "Generating API documentation..."

    if [ ! -d "$BACKEND_DIR" ]; then
        log "ERROR" "Backend directory not found at $BACKEND_DIR"
        return 1
    fi

    # Create output directory
    local api_docs_dir="$OUTPUT_DIR/api"
    mkdir -p "$api_docs_dir"

    # Check if Swagger/OpenAPI spec exists
    if [ -f "$BACKEND_DIR/openapi.yaml" ] || [ -f "$BACKEND_DIR/openapi.json" ]; then
        log "INFO" "Found OpenAPI specification"

        # Check if Swagger UI is available
        if command_exists npx; then
            log "INFO" "Generating Swagger UI documentation..."

            # Copy OpenAPI spec to output directory
            if [ -f "$BACKEND_DIR/openapi.yaml" ]; then
                cp "$BACKEND_DIR/openapi.yaml" "$api_docs_dir/"
                local spec_file="openapi.yaml"
            else
                cp "$BACKEND_DIR/openapi.json" "$api_docs_dir/"
                local spec_file="openapi.json"
            fi

            # Generate Swagger UI
            cd "$api_docs_dir"
            npx swagger-ui-dist-package "$spec_file" > index.html

            log "INFO" "Swagger UI documentation generated at $api_docs_dir/index.html"
        else
            log "WARNING" "npx not found, skipping Swagger UI generation"

            # Just copy the OpenAPI spec
            if [ -f "$BACKEND_DIR/openapi.yaml" ]; then
                cp "$BACKEND_DIR/openapi.yaml" "$api_docs_dir/"
            else
                cp "$BACKEND_DIR/openapi.json" "$api_docs_dir/"
            fi

            log "INFO" "OpenAPI specification copied to $api_docs_dir"
        fi
    else
        # Try to generate OpenAPI spec from code
        log "INFO" "No OpenAPI specification found, attempting to generate from code..."

        # Check if backend uses Flask or FastAPI
        if grep -q "fastapi" "$BACKEND_DIR/requirements.txt" 2>/dev/null; then
            log "INFO" "FastAPI detected, generating OpenAPI spec..."

            # Activate virtual environment
            source "$PROJECT_ROOT/venv/bin/activate"

            # Run script to generate OpenAPI spec
            cd "$BACKEND_DIR"
            python -c "
import sys
sys.path.insert(0, '.')
try:
    from main import app
    with open('$api_docs_dir/openapi.json', 'w') as f:
        f.write(app.openapi_json())
    print('OpenAPI spec generated successfully')
except Exception as e:
    print(f'Error generating OpenAPI spec: {e}')
    sys.exit(1)
"
            local exit_code=$?

            # Deactivate virtual environment
            deactivate

            if [ $exit_code -eq 0 ]; then
                log "INFO" "OpenAPI specification generated at $api_docs_dir/openapi.json"

                # Generate Swagger UI
                if command_exists npx; then
                    log "INFO" "Generating Swagger UI documentation..."
                    cd "$api_docs_dir"
                    npx swagger-ui-dist-package openapi.json > index.html
                    log "INFO" "Swagger UI documentation generated at $api_docs_dir/index.html"
                fi
            else
                log "ERROR" "Failed to generate OpenAPI specification"
            fi
        elif grep -q "flask" "$BACKEND_DIR/requirements.txt" 2>/dev/null; then
            log "INFO" "Flask detected, checking for Flask-RESTx or Flask-RESTPlus..."

            if grep -q "flask-restx\|flask-restplus" "$BACKEND_DIR/requirements.txt" 2>/dev/null; then
                log "INFO" "Flask-RESTx/RESTPlus detected, generating OpenAPI spec..."

                # Activate virtual environment
                source "$PROJECT_ROOT/venv/bin/activate"

                # Install flask-swagger-ui if not already installed
                pip install flask-swagger-ui

                # Run script to generate OpenAPI spec
                cd "$BACKEND_DIR"
                python -c "
import sys
sys.path.insert(0, '.')
try:
    from main import app
    with app.test_request_context():
        from flask import json
        spec = app.get_swagger_ui_blueprint()
        with open('$api_docs_dir/openapi.json', 'w') as f:
            json.dump(spec, f)
        print('OpenAPI spec generated successfully')
except Exception as e:
    print(f'Error generating OpenAPI spec: {e}')
    sys.exit(1)
"
                local exit_code=$?

                # Deactivate virtual environment
                deactivate

                if [ $exit_code -eq 0 ]; then
                    log "INFO" "OpenAPI specification generated at $api_docs_dir/openapi.json"

                    # Generate Swagger UI
                    if command_exists npx; then
                        log "INFO" "Generating Swagger UI documentation..."
                        cd "$api_docs_dir"
                        npx swagger-ui-dist-package openapi.json > index.html
                        log "INFO" "Swagger UI documentation generated at $api_docs_dir/index.html"
                    fi
                else
                    log "ERROR" "Failed to generate OpenAPI specification"
                fi
            else
                log "WARNING" "Flask detected but no RESTx/RESTPlus found, cannot generate OpenAPI spec automatically"
            fi
        else
            log "WARNING" "Could not determine API framework, skipping OpenAPI spec generation"
        fi
    fi

    # Generate API documentation from docstrings
    log "INFO" "Generating API documentation from docstrings..."

    # Check if pdoc3 is installed
    if ! command_exists pdoc3; then
        log "INFO" "Installing pdoc3..."
        pip install pdoc3
    fi

    # Generate documentation
    cd "$BACKEND_DIR"
    pdoc3 --html --output-dir "$api_docs_dir/docstrings" .

    log "INFO" "API documentation from docstrings generated at $api_docs_dir/docstrings"

    log "INFO" "API documentation generation completed"
    return 0
}

# Function to generate project status report
generate_status_report() {
    log "STEP" "Generating project status report..."

    # Create output directory
    local status_dir="$OUTPUT_DIR/status"
    mkdir -p "$status_dir"

    # Create status report file
    local report_file="$status_dir/project_status.md"

    # Write report header
    cat > "$report_file" << EOF
# CarbonXchange Project Status Report

Generated on: $(date)

## Project Overview

CarbonXchange is a blockchain-based carbon credit trading platform that leverages blockchain technology and artificial intelligence to revolutionize carbon credit trading, making it more transparent, efficient, and accessible for businesses and individuals.

## Component Status

EOF

    # Check backend status
    if [ -d "$BACKEND_DIR" ]; then
        echo "### Backend" >> "$report_file"
        echo "" >> "$report_file"

        # Count Python files
        local py_files=$(find "$BACKEND_DIR" -name "*.py" | wc -l)
        echo "- Python files: $py_files" >> "$report_file"

        # Check test coverage if pytest-cov is available
        if grep -q "pytest-cov" "$BACKEND_DIR/requirements.txt" 2>/dev/null; then
            echo "- Test coverage:" >> "$report_file"

            # Activate virtual environment
            source "$PROJECT_ROOT/venv/bin/activate"

            # Run pytest with coverage
            cd "$BACKEND_DIR"
            python -m pytest --cov=. --cov-report=term-missing > "$status_dir/backend_coverage.txt" 2>&1

            # Extract coverage percentage
            local coverage=$(grep "TOTAL" "$status_dir/backend_coverage.txt" | awk '{print $NF}')
            echo "  - Overall coverage: $coverage" >> "$report_file"

            # Deactivate virtual environment
            deactivate
        fi

        echo "" >> "$report_file"
    fi

    # Check web frontend status
    if [ -d "$WEB_FRONTEND_DIR" ]; then
        echo "### Web Frontend" >> "$report_file"
        echo "" >> "$report_file"

        # Count JS/TS files
        local js_files=$(find "$WEB_FRONTEND_DIR" -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" | wc -l)
        echo "- JavaScript/TypeScript files: $js_files" >> "$report_file"

        # Check test coverage if jest is available
        if grep -q "jest" "$WEB_FRONTEND_DIR/package.json" 2>/dev/null; then
            echo "- Test coverage:" >> "$report_file"

            # Run jest with coverage
            cd "$WEB_FRONTEND_DIR"
            npm test -- --coverage --coverageReporters="text-summary" > "$status_dir/web_frontend_coverage.txt" 2>&1

            # Extract coverage percentage
            local statements=$(grep "Statements" "$status_dir/web_frontend_coverage.txt" | awk '{print $NF}')
            local branches=$(grep "Branches" "$status_dir/web_frontend_coverage.txt" | awk '{print $NF}')
            local functions=$(grep "Functions" "$status_dir/web_frontend_coverage.txt" | awk '{print $NF}')
            local lines=$(grep "Lines" "$status_dir/web_frontend_coverage.txt" | awk '{print $NF}')

            echo "  - Statements: $statements" >> "$report_file"
            echo "  - Branches: $branches" >> "$report_file"
            echo "  - Functions: $functions" >> "$report_file"
            echo "  - Lines: $lines" >> "$report_file"
        fi

        echo "" >> "$report_file"
    fi

    # Check blockchain status
    if [ -d "$BLOCKCHAIN_DIR" ]; then
        echo "### Blockchain" >> "$report_file"
        echo "" >> "$report_file"

        # Count Solidity files
        local sol_files=$(find "$BLOCKCHAIN_DIR" -name "*.sol" | wc -l)
        echo "- Solidity files: $sol_files" >> "$report_file"

        # Check test coverage if solidity-coverage is available
        if grep -q "solidity-coverage" "$BLOCKCHAIN_DIR/package.json" 2>/dev/null; then
            echo "- Test coverage: Available via solidity-coverage" >> "$report_file"
        fi

        echo "" >> "$report_file"
    fi

    # Check mobile frontend status
    if [ -d "$MOBILE_FRONTEND_DIR" ]; then
        echo "### Mobile Frontend" >> "$report_file"
        echo "" >> "$report_file"

        # Count JS/TS files
        local js_files=$(find "$MOBILE_FRONTEND_DIR" -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" | wc -l)
        echo "- JavaScript/TypeScript files: $js_files" >> "$report_file"

        echo "" >> "$report_file"
    fi

    # Add git statistics
    echo "## Git Statistics" >> "$report_file"
    echo "" >> "$report_file"

    # Total commits
    local total_commits=$(git -C "$PROJECT_ROOT" rev-list --count HEAD)
    echo "- Total commits: $total_commits" >> "$report_file"

    # Contributors
    local contributors=$(git -C "$PROJECT_ROOT" shortlog -sn --no-merges | wc -l)
    echo "- Contributors: $contributors" >> "$report_file"

    # Recent activity
    echo "- Recent activity:" >> "$report_file"
    git -C "$PROJECT_ROOT" log --pretty=format:"  - %ad: %s" --date=short -n 5 >> "$report_file"

    echo "" >> "$report_file"
    echo "## TODO Items" >> "$report_file"
    echo "" >> "$report_file"

    # Find TODO items in code
    find "$PROJECT_ROOT" -type f -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.sol" | xargs grep -l "TODO" | while read file; do
        echo "- $file:" >> "$report_file"
        grep -n "TODO" "$file" | sed 's/^/  - Line /' >> "$report_file"
    done

    log "INFO" "Project status report generated at $report_file"
    return 0
}

# Function to generate changelog
generate_changelog() {
    log "STEP" "Generating changelog..."

    # Create output directory
    local changelog_dir="$OUTPUT_DIR/changelog"
    mkdir -p "$changelog_dir"

    # Create changelog file
    local changelog_file="$changelog_dir/CHANGELOG.md"

    # Write changelog header
    cat > "$changelog_file" << EOF
# Changelog

All notable changes to the CarbonXchange project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

EOF

    # Get git tags sorted by version
    local tags=$(git -C "$PROJECT_ROOT" tag -l | sort -V)

    if [ -z "$tags" ]; then
        log "WARNING" "No git tags found, generating changelog from commits"

        # Get all commits
        echo "## [Unreleased]" >> "$changelog_file"
        echo "" >> "$changelog_file"

        # Group commits by type
        echo "### Added" >> "$changelog_file"
        git -C "$PROJECT_ROOT" log --pretty=format:"- %s" --grep="^add" --grep="^feat" -i >> "$changelog_file"
        echo "" >> "$changelog_file"

        echo "### Changed" >> "$changelog_file"
        git -C "$PROJECT_ROOT" log --pretty=format:"- %s" --grep="^change" --grep="^update" --grep="^refactor" -i >> "$changelog_file"
        echo "" >> "$changelog_file"

        echo "### Fixed" >> "$changelog_file"
        git -C "$PROJECT_ROOT" log --pretty=format:"- %s" --grep="^fix" --grep="^bug" -i >> "$changelog_file"
        echo "" >> "$changelog_file"
    else
        log "INFO" "Found git tags, generating changelog from tags"

        # Get latest tag
        local latest_tag=$(echo "$tags" | tail -n 1)

        # Add unreleased section
        echo "## [Unreleased]" >> "$changelog_file"
        echo "" >> "$changelog_file"

        # Get commits since latest tag
        local unreleased_commits=$(git -C "$PROJECT_ROOT" log "$latest_tag"..HEAD --pretty=format:"- %s")

        if [ -n "$unreleased_commits" ]; then
            echo "$unreleased_commits" >> "$changelog_file"
        else
            echo "No unreleased changes yet." >> "$changelog_file"
        fi

        echo "" >> "$changelog_file"

        # Process each tag
        local prev_tag=""
        for tag in $tags; do
            # Get tag date
            local tag_date=$(git -C "$PROJECT_ROOT" show -s --format=%ad --date=short "$tag^{commit}")

            echo "## [$tag] - $tag_date" >> "$changelog_file"
            echo "" >> "$changelog_file"

            if [ -z "$prev_tag" ]; then
                # First tag, get all commits up to this tag
                git -C "$PROJECT_ROOT" log --pretty=format:"- %s" "$tag" >> "$changelog_file"
            else
                # Get commits between previous tag and this tag
                git -C "$PROJECT_ROOT" log --pretty=format:"- %s" "$prev_tag".."$tag" >> "$changelog_file"
            fi

            echo "" >> "$changelog_file"
            prev_tag=$tag
        done
    fi

    log "INFO" "Changelog generated at $changelog_file"
    return 0
}

# Function to validate documentation
validate_documentation() {
    log "STEP" "Validating documentation..."

    # Create output directory
    local validation_dir="$OUTPUT_DIR/validation"
    mkdir -p "$validation_dir"

    # Create validation report file
    local report_file="$validation_dir/documentation_validation.md"

    # Write report header
    cat > "$report_file" << EOF
# Documentation Validation Report

Generated on: $(date)

## Documentation Coverage

EOF

    # Check if docs directory exists
    if [ ! -d "$DOCS_DIR" ]; then
        log "WARNING" "Docs directory not found at $DOCS_DIR"
        echo "- Documentation directory not found. Consider creating a dedicated docs directory." >> "$report_file"
    else
        # Count documentation files
        local md_files=$(find "$DOCS_DIR" -name "*.md" | wc -l)
        local rst_files=$(find "$DOCS_DIR" -name "*.rst" | wc -l)
        local total_files=$((md_files + rst_files))

        echo "- Documentation files: $total_files ($md_files Markdown, $rst_files reStructuredText)" >> "$report_file"

        # Check for README files
        echo "## README Files" >> "$report_file"

        if [ -f "$PROJECT_ROOT/README.md" ]; then
            echo "- Main README.md: ✅ Present" >> "$report_file"
        else
            echo "- Main README.md: ❌ Missing" >> "$report_file"
        fi

        # Check for component READMEs
        for dir in "$BACKEND_DIR" "$BLOCKCHAIN_DIR" "$WEB_FRONTEND_DIR" "$MOBILE_FRONTEND_DIR"; do
            if [ -d "$dir" ]; then
                local dir_name=$(basename "$dir")
                if [ -f "$dir/README.md" ]; then
                    echo "- $dir_name README.md: ✅ Present" >> "$report_file"
                else
                    echo "- $dir_name README.md: ❌ Missing" >> "$report_file"
                fi
            fi
        done

        echo "" >> "$report_file"
        echo "## API Documentation" >> "$report_file"

        # Check for API documentation
        if [ -f "$BACKEND_DIR/openapi.yaml" ] || [ -f "$BACKEND_DIR/openapi.json" ]; then
            echo "- OpenAPI Specification: ✅ Present" >> "$report_file"
        else
            echo "- OpenAPI Specification: ❌ Missing" >> "$report_file"
        fi

        # Check for docstrings in Python files
        local py_files_with_docstrings=$(find "$BACKEND_DIR" -name "*.py" -exec grep -l '"""' {} \; | wc -l)
        local total_py_files=$(find "$BACKEND_DIR" -name "*.py" | wc -l)

        if [ $total_py_files -gt 0 ]; then
            local docstring_percentage=$((py_files_with_docstrings * 100 / total_py_files))
            echo "- Python docstrings: $docstring_percentage% ($py_files_with_docstrings out of $total_py_files files)" >> "$report_file"
        else
            echo "- Python docstrings: N/A (no Python files found)" >> "$report_file"
        fi

        echo "" >> "$report_file"
        echo "## Documentation Quality" >> "$report_file"

        # Check for broken links in Markdown files
        echo "### Broken Links" >> "$report_file"

        find "$DOCS_DIR" -name "*.md" -exec grep -l "\[.*\](.*)" {} \; | while read file; do
            local broken_links=$(grep -o "\[.*\](.*)" "$file" | grep -v "^http" | grep -v "^#" | grep -v "^mailto:")
            if [ -n "$broken_links" ]; then
                echo "- $file:" >> "$report_file"
                echo "$broken_links" | sed 's/^/  - /' >> "$report_file"
            fi
        done

        # Check for outdated documentation
        echo "### Potentially Outdated Documentation" >> "$report_file"

        find "$DOCS_DIR" -name "*.md" -mtime +90 | while read file; do
            local last_modified=$(stat -c %y "$file" | cut -d ' ' -f 1)
            echo "- $file (Last modified: $last_modified)" >> "$report_file"
        done
    fi

    log "INFO" "Documentation validation report generated at $report_file"
    return 0
}

# Function to generate component documentation
generate_component_docs() {
    log "STEP" "Generating component documentation..."

    # Create output directory
    local component_docs_dir="$OUTPUT_DIR/components"
    mkdir -p "$component_docs_dir"

    # Backend documentation
    if [ -d "$BACKEND_DIR" ]; then
        log "INFO" "Generating backend component documentation..."

        local backend_docs_dir="$component_docs_dir/backend"
        mkdir -p "$backend_docs_dir"

        # Create backend documentation file
        local backend_doc_file="$backend_docs_dir/README.md"

        # Write documentation header
        cat > "$backend_doc_file" << EOF
# Backend Component Documentation

Generated on: $(date)

## Overview

The backend component of CarbonXchange provides the API and core business logic for the platform.

## Directory Structure

\`\`\`
EOF

        # Add directory structure
        find "$BACKEND_DIR" -type d | sort | sed "s|$BACKEND_DIR|.|" >> "$backend_doc_file"

        # Close code block
        echo '```' >> "$backend_doc_file"

        # Add module information
        echo "" >> "$backend_doc_file"
        echo "## Modules" >> "$backend_doc_file"
        echo "" >> "$backend_doc_file"

        find "$BACKEND_DIR" -name "*.py" -not -path "*/\.*" -not -path "*/venv/*" | sort | while read file; do
            local rel_path=${file#$BACKEND_DIR/}
            echo "### $rel_path" >> "$backend_doc_file"
            echo "" >> "$backend_doc_file"

            # Extract module docstring
            local docstring=$(grep -A 10 '"""' "$file" | grep -v '"""' | grep -B 10 -m 1 '"""' || echo "No docstring found.")

            echo "```python" >> "$backend_doc_file"
            echo "$docstring" >> "$backend_doc_file"
            echo "```" >> "$backend_doc_file"
            echo "" >> "$backend_doc_file"
        done
    fi

    # Web frontend documentation
    if [ -d "$WEB_FRONTEND_DIR" ]; then
        log "INFO" "Generating web frontend component documentation..."

        local frontend_docs_dir="$component_docs_dir/web-frontend"
        mkdir -p "$frontend_docs_dir"

        # Create frontend documentation file
        local frontend_doc_file="$frontend_docs_dir/README.md"

        # Write documentation header
        cat > "$frontend_doc_file" << EOF
# Web Frontend Component Documentation

Generated on: $(date)

## Overview

The web frontend component of CarbonXchange provides the user interface for the platform.

## Directory Structure

\`\`\`
EOF

        # Add directory structure
        find "$WEB_FRONTEND_DIR" -type d | sort | sed "s|$WEB_FRONTEND_DIR|.|" >> "$frontend_doc_file"

        # Close code block
        echo '```' >> "$frontend_doc_file"

        # Add component information
        echo "" >> "$frontend_doc_file"
        echo "## Components" >> "$frontend_doc_file"
        echo "" >> "$frontend_doc_file"

        find "$WEB_FRONTEND_DIR/src" -name "*.jsx" -o -name "*.tsx" | sort | while read file; do
            local rel_path=${file#$WEB_FRONTEND_DIR/}
            echo "### $rel_path" >> "$frontend_doc_file"
            echo "" >> "$frontend_doc_file"

            # Extract component description
            local description=$(grep -A 10 '/\*\*' "$file" | grep -v '/\*\*' | grep -B 10 -m 1 '\*/' || echo "No description found.")

            echo "```jsx" >> "$frontend_doc_file"
            echo "$description" >> "$frontend_doc_file"
            echo "```" >> "$frontend_doc_file"
            echo "" >> "$frontend_doc_file"
        done
    fi

    log "INFO" "Component documentation generated at $component_docs_dir"
    return 0
}

# Function to display help message
show_help() {
    echo "CarbonXchange Documentation Generator"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --help, -h                 Show this help message"
    echo "  --all                      Generate all documentation"
    echo "  --api                      Generate API documentation"
    echo "  --status                   Generate project status report"
    echo "  --changelog                Generate changelog"
    echo "  --validate                 Validate existing documentation"
    echo "  --components               Generate component documentation"
    echo ""
    echo "Examples:"
    echo "  $0 --all                   Generate all documentation"
    echo "  $0 --api --status          Generate API documentation and project status report"
}

# Main function
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    local gen_api=false
    local gen_status=false
    local gen_changelog=false
    local validate_docs=false
    local gen_components=false
    local gen_all=false

    # Parse command line arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --help|-h)
                show_help
                exit 0
                ;;
            --all)
                gen_all=true
                ;;
            --api)
                gen_api=true
                ;;
            --status)
                gen_status=true
                ;;
            --changelog)
                gen_changelog=true
                ;;
            --validate)
                validate_docs=true
                ;;
            --components)
                gen_components=true
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
    if [ "$gen_all" = true ]; then
        gen_api=true
        gen_status=true
        gen_changelog=true
        validate_docs=true
        gen_components=true
    fi

    # Print banner
    echo "========================================================"
    echo "  CarbonXchange Documentation Generator"
    echo "========================================================"
    echo ""

    # Generate documentation based on options
    if [ "$gen_api" = true ]; then
        generate_api_docs
    fi

    if [ "$gen_status" = true ]; then
        generate_status_report
    fi

    if [ "$gen_changelog" = true ]; then
        generate_changelog
    fi

    if [ "$validate_docs" = true ]; then
        validate_documentation
    fi

    if [ "$gen_components" = true ]; then
        generate_component_docs
    fi

    log "INFO" "Documentation generation completed"
    echo ""
    log "INFO" "Generated documentation available in: $OUTPUT_DIR"
    echo ""
}

# Run main function
main "$@"
