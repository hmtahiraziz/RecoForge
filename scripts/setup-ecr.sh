#!/bin/bash
set -e

# Configuration
AWS_REGION="us-east-1"
PROJECT_NAME="single-app-host"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on EC2
check_ec2() {
    if ! curl -s --max-time 5 http://169.254.169.254/latest/meta-data/instance-id > /dev/null; then
        log_error "This script must be run on an EC2 instance"
        exit 1
    fi
}

# Get AWS account ID
get_account_id() {
    aws sts get-caller-identity --query Account --output text
}

# Get ECR registry URL
get_ecr_registry() {
    local account_id=$(get_account_id)
    echo "${account_id}.dkr.ecr.${AWS_REGION}.amazonaws.com"
}

# Check if ECR repositories exist
check_ecr_repos() {
    local registry=$(get_ecr_registry)

    log_info "Checking ECR repositories..."

    # Check API repository
    if aws ecr describe-repositories --repository-names "${PROJECT_NAME}-api" --region $AWS_REGION > /dev/null 2>&1; then
        log_info "API repository exists: ${registry}/${PROJECT_NAME}-api"
    else
        log_error "API repository not found: ${PROJECT_NAME}-api"
        return 1
    fi

    # Check Web repository (optional)
    if aws ecr describe-repositories --repository-names "${PROJECT_NAME}-web" --region $AWS_REGION > /dev/null 2>&1; then
        log_info "Web repository exists: ${registry}/${PROJECT_NAME}-web"
    else
        log_warn "Web repository not found: ${PROJECT_NAME}-web (optional)"
    fi
}

# Login to ECR
ecr_login() {
    log_info "Logging in to ECR..."
    local registry=$(get_ecr_registry)
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $registry
    log_info "Successfully logged in to ECR"
}

# Test ECR access
test_ecr_access() {
    local registry=$(get_ecr_registry)

    log_info "Testing ECR access..."

    # Test API repository access
    if aws ecr describe-images --repository-name "${PROJECT_NAME}-api" --region $AWS_REGION > /dev/null 2>&1; then
        log_info "API repository access confirmed"
    else
        log_warn "API repository access failed or no images found"
    fi

    # Test Web repository access (if exists)
    if aws ecr describe-repositories --repository-names "${PROJECT_NAME}-web" --region $AWS_REGION > /dev/null 2>&1; then
        if aws ecr describe-images --repository-name "${PROJECT_NAME}-web" --region $AWS_REGION > /dev/null 2>&1; then
            log_info "Web repository access confirmed"
        else
            log_warn "Web repository access failed or no images found"
        fi
    fi
}

# Show ECR information
show_ecr_info() {
    local registry=$(get_ecr_registry)
    local account_id=$(get_account_id)

    log_info "ECR Configuration:"
    echo "==================="
    echo "Account ID: $account_id"
    echo "Region: $AWS_REGION"
    echo "Registry URL: $registry"
    echo "API Repository: $registry/${PROJECT_NAME}-api"
    echo "Web Repository: $registry/${PROJECT_NAME}-web"
    echo ""

    # Show available images
    log_info "Available Images:"
    echo "=================="

    # API images
    echo "API Images:"
    aws ecr describe-images --repository-name "${PROJECT_NAME}-api" --region $AWS_REGION --query 'imageDetails[*].imageTags[0]' --output table 2>/dev/null || echo "No API images found"
    echo ""

    # Web images
    if aws ecr describe-repositories --repository-names "${PROJECT_NAME}-web" --region $AWS_REGION > /dev/null 2>&1; then
        echo "Web Images:"
        aws ecr describe-images --repository-name "${PROJECT_NAME}-web" --region $AWS_REGION --query 'imageDetails[*].imageTags[0]' --output table 2>/dev/null || echo "No Web images found"
    fi
}

# Create docker-compose override for ECR
create_ecr_compose() {
    local registry=$(get_ecr_registry)

    log_info "Creating docker-compose.ecr.yml override..."

    cat > /opt/app/app/docker-compose.ecr.yml << EOF
version: '3.8'

services:
  api:
    image: ${registry}/${PROJECT_NAME}-api:latest
    build: null  # Disable local build

  web:
    image: ${registry}/${PROJECT_NAME}-web:latest
    build: null  # Disable local build
EOF

    log_info "Created docker-compose.ecr.yml"
    log_info "Use 'docker compose -f docker-compose.yml -f docker-compose.ecr.yml up -d' to use ECR images"
}

# Main setup function
setup_ecr() {
    log_info "Setting up ECR integration at $(date)"

    # Check prerequisites
    check_ec2

    # Check ECR repositories
    check_ecr_repos

    # Login to ECR
    ecr_login

    # Test access
    test_ecr_access

    # Show information
    show_ecr_info

    # Create ECR compose override
    create_ecr_compose

    log_info "ECR setup completed successfully"
}

# Show usage
usage() {
    echo "Usage: $0 [setup|info|login|test]"
    echo ""
    echo "Commands:"
    echo "  setup - Complete ECR setup and configuration"
    echo "  info  - Show ECR repository information"
    echo "  login - Login to ECR"
    echo "  test  - Test ECR access"
    echo ""
}

# Main script logic
case "${1:-setup}" in
    setup)
        setup_ecr
        ;;
    info)
        check_ec2
        show_ecr_info
        ;;
    login)
        check_ec2
        ecr_login
        ;;
    test)
        check_ec2
        test_ecr_access
        ;;
    *)
        usage
        exit 1
        ;;
esac
