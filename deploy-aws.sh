#!/bin/bash
set -e

# Configuration
AWS_REGION="ap-southeast-2"
AWS_PROFILE="AWSAdministratorAccess-149999906241"
ECR_REGISTRY="149999906241.dkr.ecr.ap-southeast-2.amazonaws.com"
ECR_REPOSITORY="my-app-host-api"
EC2_HOST="54.79.178.51"
SSH_KEY="~/.ssh/id_ed25519"

# Git Configuration
GIT_REPO="git@code.visualr.space:hackathon/01/team-01.git"  # UPDATE THIS
GIT_BRANCH="staging"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi

    # Test AWS access with the correct profile
    if ! aws sts get-caller-identity --profile $AWS_PROFILE >/dev/null 2>&1; then
        log_error "AWS credentials are not working. Please run: aws sso login --profile $AWS_PROFILE"
        exit 1
    fi

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi

    if [ ! -f ~/.ssh/id_ed25519 ]; then
        log_error "SSH key not found at ~/.ssh/id_ed25519"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

# Login to ECR
ecr_login() {
    log_step "Logging in to ECR..."
    aws ecr get-login-password --region $AWS_REGION --profile $AWS_PROFILE | docker login --username AWS --password-stdin $ECR_REGISTRY
    log_info "ECR login successful"
}

# Build and push backend image
build_and_push_backend() {
    log_step "Building and pushing backend image..."

    # Build the image
    docker build -t $ECR_REPOSITORY:latest ./app

    # Tag for ECR
    docker tag $ECR_REPOSITORY:latest $ECR_REGISTRY/$ECR_REPOSITORY:latest

    # Push to ECR
    docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

    log_info "Backend image pushed to ECR"
}

# Deploy to EC2 using Git
# Deploy to EC2 using Git
deploy_to_ec2() {
    log_step "Deploying to EC2 instance using Git..."

    # SSH into EC2 and deploy
    ssh -i $SSH_KEY ubuntu@$EC2_HOST << EOF
        set -e

        echo "=== Setting up deployment environment ==="

        # Create app directory with proper permissions
        sudo mkdir -p /opt/app
        sudo chown -R ubuntu:ubuntu /opt/app
        cd /opt/app

        # Install git if not present
        if ! command -v git &> /dev/null; then
            echo "Installing git..."
            sudo apt-get update && sudo apt-get install -y git
        fi

        # Install docker-compose if not present
        if ! command -v docker-compose &> /dev/null; then
            echo "Installing docker-compose..."
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
        fi

        # Clone or update repository
        if [ -d "app-source" ]; then
            echo "Updating existing repository..."
            cd app-source
            git fetch origin
            git reset --hard origin/$GIT_BRANCH
            git clean -fd
        else
            echo "Cloning repository..."
            git clone $GIT_REPO app-source
            cd app-source
            git checkout $GIT_BRANCH
        fi

        echo "=== Setting up environment files ==="

        # Copy environment file if it doesn't exist
        if [ ! -f ".env" ]; then
            echo "Creating .env file from template..."
            cp env.production .env || echo "No env.production found, using defaults"
        fi

        # Ensure docker-compose.yml exists
        if [ ! -f "docker-compose.yml" ]; then
            echo "Creating docker-compose.yml from production template..."
            cp docker-compose.prod.yml docker-compose.yml || echo "No docker-compose.prod.yml found"
        fi

        echo "=== Setting up data directories and files ==="

        # Create data and index directories
        mkdir -p data index

        # Copy products data file if it exists
        if [ -f "products-data.json" ]; then
            echo "Copying products-data.json to data directory..."
            cp products-data.json data/products-data.json
            echo "Products data file copied successfully"
        else
            echo "Warning: products-data.json not found in repository"
        fi

        # Set proper permissions for data directories
        chmod -R 755 data index

        echo "=== Building and deploying application ==="

        # Login to ECR using instance role (no profile needed)
        aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

        # Stop existing containers
        docker-compose down || true

        # Pull latest backend image
        docker pull $ECR_REGISTRY/$ECR_REPOSITORY:latest

        # Build and start services
        docker-compose up -d --build

        # Wait for services to be healthy
        echo "Waiting for services to start..."
        sleep 30

        # Check health
        docker-compose ps
        docker-compose logs --tail=20 backend

        echo "=== Deployment completed ==="
EOF

    log_info "Git-based deployment completed"
}

# Test deployment
test_deployment() {
    log_step "Testing deployment..."

    # Test backend health
    log_info "Testing backend health endpoint..."
    curl -f http://$EC2_HOST:8000/health || log_warn "Backend health check failed"

    # Test frontend
    log_info "Testing frontend..."
    curl -f http://$EC2_HOST:3000 || log_warn "Frontend check failed"

    log_info "Deployment test completed"
}

# Main deployment function
main() {
    log_info "Starting AWS deployment..."

    check_prerequisites
    ecr_login
    build_and_push_backend
    deploy_to_ec2
    test_deployment

    log_info "Deployment completed successfully!"
    log_info "Your application is available at:"
    log_info "  Frontend: http://$EC2_HOST:3000"
    log_info "  Backend API: http://$EC2_HOST:8000"
    log_info "  GraphQL Playground: http://$EC2_HOST:8000/graphql"
    log_info "  API Docs: http://$EC2_HOST:8000/docs"
}

# Run main function
main "$@"