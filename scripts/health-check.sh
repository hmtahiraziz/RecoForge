#!/bin/bash
set -e

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

log_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# System health checks
check_system() {
    log_header "System Health Check"
    echo "====================="

    # Uptime
    echo "System Uptime: $(uptime)"
    echo ""

    # Memory usage
    echo "Memory Usage:"
    free -h
    echo ""

    # Disk usage
    echo "Disk Usage:"
    df -h
    echo ""

    # Load average
    echo "Load Average:"
    cat /proc/loadavg
    echo ""

    # CPU info
    echo "CPU Information:"
    lscpu | grep -E "Model name|CPU\(s\)|Thread|Core"
    echo ""
}

# Docker health checks
check_docker() {
    log_header "Docker Health Check"
    echo "====================="

    # Docker service status
    if systemctl is-active --quiet docker; then
        log_info "Docker service is running"
    else
        log_error "Docker service is not running"
        return 1
    fi

    # Docker version
    echo "Docker Version:"
    docker --version
    docker compose version
    echo ""

    # Docker system info
    echo "Docker System Info:"
    docker system df
    echo ""

    # Running containers
    echo "Running Containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
}

# Application health checks
check_application() {
    log_header "Application Health Check"
    echo "=========================="

    # Check if app directory exists
    if [ ! -d "/opt/app/app" ]; then
        log_error "Application directory not found: /opt/app/app"
        return 1
    fi

    cd /opt/app/app

    # Check docker-compose status
    if [ -f "docker-compose.yml" ]; then
        echo "Docker Compose Status:"
        docker compose ps
        echo ""

        # Check if services are running
        if docker compose ps | grep -q "Up"; then
            log_info "Application services are running"
        else
            log_error "Some application services are not running"
        fi
    else
        log_warn "docker-compose.yml not found"
    fi

    # Test API endpoint
    echo "API Health Check:"
    if curl -f -s --max-time 10 http://localhost:8000/health > /dev/null 2>&1; then
        log_info "API health endpoint is responding"
    elif curl -f -s --max-time 10 http://localhost:8000 > /dev/null 2>&1; then
        log_info "API is responding (no health endpoint)"
    else
        log_warn "API is not responding on port 8000"
    fi
    echo ""

    # Test web app
    echo "Web App Health Check:"
    if curl -f -s --max-time 10 http://localhost:3000 > /dev/null 2>&1; then
        log_info "Web app is responding"
    else
        log_warn "Web app is not responding on port 3000"
    fi
    echo ""
}

# Caddy health checks
check_caddy() {
    log_header "Caddy Health Check"
    echo "==================="

    # Caddy service status
    if systemctl is-active --quiet caddy; then
        log_info "Caddy service is running"
    else
        log_error "Caddy service is not running"
        return 1
    fi

    # Caddy version
    echo "Caddy Version:"
    caddy version
    echo ""

    # Caddy configuration
    if [ -f "/etc/caddy/Caddyfile" ]; then
        echo "Caddy Configuration:"
        cat /etc/caddy/Caddyfile
        echo ""

        # Test Caddyfile syntax
        if caddy validate --config /etc/caddy/Caddyfile 2>/dev/null; then
            log_info "Caddyfile syntax is valid"
        else
            log_warn "Caddyfile syntax may have issues"
        fi
    else
        log_warn "Caddyfile not found"
    fi

    # Test external access
    echo "External Access Test:"
    local public_ip=$(curl -s --max-time 10 https://checkip.amazonaws.com || echo "Unable to get public IP")
    echo "Public IP: $public_ip"

    if curl -f -s --max-time 10 http://$public_ip > /dev/null 2>&1; then
        log_info "External HTTP access is working"
    else
        log_warn "External HTTP access may not be working"
    fi
    echo ""
}

# AWS health checks
check_aws() {
    log_header "AWS Health Check"
    echo "================="

    # Check if running on EC2
    if curl -s --max-time 5 http://169.254.169.254/latest/meta-data/instance-id > /dev/null; then
        local instance_id=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
        local instance_type=$(curl -s http://169.254.169.254/latest/meta-data/instance-type)
        local availability_zone=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)

        log_info "Running on EC2 instance: $instance_id"
        echo "Instance Type: $instance_type"
        echo "Availability Zone: $availability_zone"
        echo ""

        # Check AWS CLI
        if command -v aws > /dev/null; then
            echo "AWS CLI Version:"
            aws --version
            echo ""

            # Check AWS credentials
            if aws sts get-caller-identity > /dev/null 2>&1; then
                log_info "AWS credentials are working"
                echo "AWS Account Info:"
                aws sts get-caller-identity
                echo ""
            else
                log_warn "AWS credentials may not be working"
            fi
        else
            log_warn "AWS CLI not found"
        fi
    else
        log_warn "Not running on EC2 instance"
    fi
}

# Network health checks
check_network() {
    log_header "Network Health Check"
    echo "======================"

    # Check network interfaces
    echo "Network Interfaces:"
    ip addr show | grep -E "inet |UP|DOWN"
    echo ""

    # Check listening ports
    echo "Listening Ports:"
    netstat -tlnp | grep -E ":22|:80|:443|:3000|:8000"
    echo ""

    # Test DNS resolution
    echo "DNS Resolution Test:"
    if nslookup google.com > /dev/null 2>&1; then
        log_info "DNS resolution is working"
    else
        log_warn "DNS resolution may have issues"
    fi
    echo ""
}

# Security health checks
check_security() {
    log_header "Security Health Check"
    echo "======================="

    # Check SSH configuration
    echo "SSH Service Status:"
    systemctl status ssh --no-pager -l
    echo ""

    # Check firewall (if ufw is installed)
    if command -v ufw > /dev/null; then
        echo "UFW Status:"
        ufw status
        echo ""
    fi

    # Check for security updates
    echo "Security Updates:"
    if command -v apt > /dev/null; then
        apt list --upgradable 2>/dev/null | grep -i security | head -5 || echo "No security updates available"
    fi
    echo ""
}

# Generate health report
generate_report() {
    local report_file="/opt/app/health-report-$(date +%Y%m%d-%H%M%S).txt"

    log_info "Generating health report: $report_file"

    {
        echo "Health Check Report - $(date)"
        echo "=============================="
        echo ""

        check_system
        check_docker
        check_application
        check_caddy
        check_aws
        check_network
        check_security

    } > "$report_file"

    log_info "Health report saved to: $report_file"
}

# Main health check function
run_health_check() {
    log_info "Starting comprehensive health check at $(date)"
    echo "=============================================="
    echo ""

    check_system
    check_docker
    check_application
    check_caddy
    check_aws
    check_network
    check_security

    log_info "Health check completed at $(date)"
}

# Show usage
usage() {
    echo "Usage: $0 [check|report|system|docker|app|caddy|aws|network|security]"
    echo ""
    echo "Commands:"
    echo "  check    - Run comprehensive health check (default)"
    echo "  report   - Generate detailed health report file"
    echo "  system   - Check system resources"
    echo "  docker   - Check Docker status"
    echo "  app      - Check application status"
    echo "  caddy    - Check Caddy status"
    echo "  aws      - Check AWS integration"
    echo "  network  - Check network connectivity"
    echo "  security - Check security configuration"
    echo ""
}

# Main script logic
case "${1:-check}" in
    check)
        run_health_check
        ;;
    report)
        generate_report
        ;;
    system)
        check_system
        ;;
    docker)
        check_docker
        ;;
    app)
        check_application
        ;;
    caddy)
        check_caddy
        ;;
    aws)
        check_aws
        ;;
    network)
        check_network
        ;;
    security)
        check_security
        ;;
    *)
        usage
        exit 1
        ;;
esac
