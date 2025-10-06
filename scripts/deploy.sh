#!/bin/bash
set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REGISTRY=""
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

# Login to ECR
ecr_login() {
    log_info "Logging in to ECR..."
    local registry=$(get_ecr_registry)
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $registry
    ECR_REGISTRY=$registry
}

# Pull latest images
pull_images() {
    log_info "Pulling latest images..."
    docker compose pull
}

# Restart services
restart_services() {
    log_info "Restarting services..."
    docker compose up -d
}

# Clean up old images
cleanup_images() {
    log_info "Cleaning up old Docker images..."
    docker image prune -f
}

# Health check
health_check() {
    log_info "Performing health check..."

    # Wait for services to start
    sleep 10

    # Check if containers are running
    if ! docker compose ps | grep -q "Up"; then
        log_error "Some containers are not running"
        docker compose ps
        return 1
    fi

    # Test API endpoint (if available)
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        log_info "API health check passed"
    else
        log_warn "API health check failed or endpoint not available"
    fi

    # Test web app
    if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
        log_info "Web app health check passed"
    else
        log_warn "Web app health check failed"
    fi
}

# Show deployment status
show_status() {
    log_info "Deployment Status:"
    echo "==================="
    docker compose ps
    echo ""
    log_info "Recent logs:"
    docker compose logs --tail=20
}

# Main deployment function
deploy() {
    log_info "Starting deployment at $(date)"

    # Check prerequisites
    check_ec2

    # Change to app directory
    cd /opt/app/app

    # ECR login
    ecr_login

    # Pull and restart
    pull_images
    restart_services

    # Cleanup
    cleanup_images

    # Health check
    health_check

    # Show status
    show_status

    log_info "Deployment completed successfully at $(date)"
}

# Rollback function
rollback() {
    log_info "Rolling back to previous version..."

    cd /opt/app/app

    # Get previous image tags
    local api_prev=$(docker images --format "table {{.Tag}}" | grep -v "latest" | head -2 | tail -1)
    local web_prev=$(docker images --format "table {{.Tag}}" | grep -v "latest" | head -2 | tail -1)

    if [ -z "$api_prev" ] || [ -z "$web_prev" ]; then
        log_error "No previous versions found for rollback"
        exit 1
    fi

    # Update docker-compose.yml to use previous tags
    sed -i "s/:latest/:$api_prev/g" docker-compose.yml
    sed -i "s/:latest/:$web_prev/g" docker-compose.yml

    # Restart with previous images
    docker compose up -d

    log_info "Rollback completed"
}

# Show usage
usage() {
    echo "Usage: $0 [deploy|rollback|status|health]"
    echo ""
    echo "Commands:"
    echo "  deploy   - Deploy latest images from ECR"
    echo "  rollback - Rollback to previous version"
    echo "  status   - Show current deployment status"
    echo "  health   - Run health checks"
    echo ""
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    status)
        cd /opt/app/app
        show_status
        ;;
    health)
        cd /opt/app/app
        health_check
        ;;
    *)
        usage
        exit 1
        ;;
esac
