#!/bin/bash

# CarbonXchange Infrastructure Deployment Script
# This script deploys the comprehensive infrastructure for financial compliance

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-staging}"
TERRAFORM_DIR="$INFRA_DIR/terraform"
KUBERNETES_DIR="$INFRA_DIR/kubernetes"
ANSIBLE_DIR="$INFRA_DIR/ansible"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validation functions
validate_environment() {
    if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
        log_error "Invalid environment: $ENVIRONMENT. Must be dev, staging, or prod."
        exit 1
    fi
}

validate_prerequisites() {
    log_info "Validating prerequisites..."
    
    # Check required tools
    local tools=("terraform" "kubectl" "ansible" "aws")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is not installed or not in PATH"
            exit 1
        fi
    done
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured or invalid"
        exit 1
    fi
    
    # Check Terraform version
    local tf_version=$(terraform version -json | jq -r '.terraform_version')
    if [[ $(echo "$tf_version 1.5.0" | tr " " "\n" | sort -V | head -n1) != "1.5.0" ]]; then
        log_error "Terraform version must be 1.5.0 or higher. Current: $tf_version"
        exit 1
    fi
    
    log_success "Prerequisites validated"
}

validate_terraform_config() {
    log_info "Validating Terraform configuration..."
    
    cd "$TERRAFORM_DIR"
    
    # Check if tfvars file exists
    local tfvars_file="environments/$ENVIRONMENT/terraform.tfvars"
    if [[ ! -f "$tfvars_file" ]]; then
        log_error "Terraform variables file not found: $tfvars_file"
        exit 1
    fi
    
    # Validate Terraform configuration
    terraform init -backend=false &> /dev/null
    if ! terraform validate; then
        log_error "Terraform configuration validation failed"
        exit 1
    fi
    
    log_success "Terraform configuration validated"
}

# Deployment functions
deploy_terraform() {
    log_info "Deploying Terraform infrastructure for $ENVIRONMENT..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    log_info "Creating Terraform plan..."
    terraform plan -var-file="environments/$ENVIRONMENT/terraform.tfvars" -out="$ENVIRONMENT.tfplan"
    
    # Ask for confirmation in production
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        echo
        log_warning "You are about to deploy to PRODUCTION environment!"
        read -p "Are you sure you want to continue? (yes/no): " confirm
        if [[ "$confirm" != "yes" ]]; then
            log_info "Deployment cancelled"
            exit 0
        fi
    fi
    
    # Apply configuration
    log_info "Applying Terraform configuration..."
    terraform apply "$ENVIRONMENT.tfplan"
    
    # Clean up plan file
    rm -f "$ENVIRONMENT.tfplan"
    
    log_success "Terraform infrastructure deployed"
}

deploy_kubernetes() {
    log_info "Deploying Kubernetes configurations for $ENVIRONMENT..."
    
    cd "$KUBERNETES_DIR"
    
    # Create namespace if it doesn't exist
    kubectl create namespace "carbonxchange-$ENVIRONMENT" --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply security configurations first
    log_info "Applying security policies..."
    kubectl apply -f security/ -n "carbonxchange-$ENVIRONMENT"
    
    # Apply base configurations
    log_info "Applying base configurations..."
    kubectl apply -f base/ -n "carbonxchange-$ENVIRONMENT"
    
    # Apply monitoring configurations
    log_info "Applying monitoring configurations..."
    kubectl apply -f monitoring/ -n "carbonxchange-$ENVIRONMENT"
    
    # Apply compliance configurations
    log_info "Applying compliance configurations..."
    kubectl apply -f compliance/ -n "carbonxchange-$ENVIRONMENT"
    
    # Apply environment-specific configurations
    if [[ -d "environments/$ENVIRONMENT" ]]; then
        log_info "Applying environment-specific configurations..."
        kubectl apply -f "environments/$ENVIRONMENT/" -n "carbonxchange-$ENVIRONMENT"
    fi
    
    log_success "Kubernetes configurations deployed"
}

deploy_ansible() {
    log_info "Running Ansible playbooks for $ENVIRONMENT..."
    
    cd "$ANSIBLE_DIR"
    
    # Check if inventory file exists
    local inventory_file="inventory/hosts.yml"
    if [[ ! -f "$inventory_file" ]]; then
        log_warning "Ansible inventory file not found: $inventory_file. Skipping Ansible deployment."
        return 0
    fi
    
    # Run main playbook
    ansible-playbook -i "$inventory_file" playbooks/main.yml --extra-vars "environment=$ENVIRONMENT"
    
    log_success "Ansible playbooks executed"
}

# Verification functions
verify_deployment() {
    log_info "Verifying deployment for $ENVIRONMENT..."
    
    # Verify Terraform resources
    cd "$TERRAFORM_DIR"
    log_info "Verifying Terraform resources..."
    terraform show -json > "/tmp/terraform-state-$ENVIRONMENT.json"
    
    # Verify Kubernetes resources
    log_info "Verifying Kubernetes resources..."
    kubectl get all -n "carbonxchange-$ENVIRONMENT"
    
    # Check pod status
    local failed_pods=$(kubectl get pods -n "carbonxchange-$ENVIRONMENT" --field-selector=status.phase!=Running --no-headers 2>/dev/null | wc -l)
    if [[ "$failed_pods" -gt 0 ]]; then
        log_warning "$failed_pods pods are not in Running state"
        kubectl get pods -n "carbonxchange-$ENVIRONMENT" --field-selector=status.phase!=Running
    fi
    
    # Verify security policies
    log_info "Verifying security policies..."
    kubectl get psp,networkpolicy -n "carbonxchange-$ENVIRONMENT"
    
    log_success "Deployment verification completed"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    rm -f "/tmp/terraform-state-$ENVIRONMENT.json"
    cd "$TERRAFORM_DIR" && rm -f "$ENVIRONMENT.tfplan"
}

# Main deployment function
main() {
    log_info "Starting CarbonXchange infrastructure deployment"
    log_info "Environment: $ENVIRONMENT"
    log_info "Timestamp: $(date)"
    
    # Validation phase
    validate_environment
    validate_prerequisites
    validate_terraform_config
    
    # Deployment phase
    deploy_terraform
    deploy_kubernetes
    deploy_ansible
    
    # Verification phase
    verify_deployment
    
    # Cleanup
    cleanup
    
    log_success "CarbonXchange infrastructure deployment completed successfully!"
    log_info "Environment: $ENVIRONMENT"
    log_info "Deployment completed at: $(date)"
    
    # Display important information
    echo
    log_info "Important URLs and Information:"
    echo "  - AWS Console: https://console.aws.amazon.com/"
    echo "  - Kubernetes Dashboard: kubectl proxy"
    echo "  - Monitoring: Check CloudWatch dashboards"
    echo "  - Logs: CloudWatch Logs groups"
    echo
    log_info "Next steps:"
    echo "  1. Verify application deployment"
    echo "  2. Run security scans"
    echo "  3. Validate compliance requirements"
    echo "  4. Update documentation"
}

# Error handling
trap cleanup EXIT
trap 'log_error "Deployment failed at line $LINENO"' ERR

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

