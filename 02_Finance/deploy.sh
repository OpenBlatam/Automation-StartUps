#!/bin/bash

# Frontier AI Deployment Script
# Automated deployment script for production environments

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-production}"
VERSION="${2:-latest}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-ghcr.io}"
IMAGE_NAME="${IMAGE_NAME:-frontier-ai}"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if kubectl is installed (for Kubernetes deployment)
    if [ "$ENVIRONMENT" = "kubernetes" ] && ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Backup current deployment
backup_deployment() {
    log_info "Creating backup of current deployment..."
    
    BACKUP_DIR="$PROJECT_DIR/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup configuration files
    cp -r "$PROJECT_DIR"/configs "$BACKUP_DIR/" 2>/dev/null || true
    cp "$PROJECT_DIR"/docker-compose.yml "$BACKUP_DIR/" 2>/dev/null || true
    cp "$PROJECT_DIR"/.env "$BACKUP_DIR/" 2>/dev/null || true
    
    # Backup database (if PostgreSQL is running)
    if docker ps | grep -q postgres; then
        log_info "Backing up database..."
        docker exec frontier-postgres pg_dump -U frontier frontier_ai > "$BACKUP_DIR/database_backup.sql"
    fi
    
    log_success "Backup created at $BACKUP_DIR"
}

# Pull latest images
pull_images() {
    log_info "Pulling latest Docker images..."
    
    # Login to registry if credentials are provided
    if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
        echo "$DOCKER_PASSWORD" | docker login "$DOCKER_REGISTRY" -u "$DOCKER_USERNAME" --password-stdin
    fi
    
    # Pull images
    docker-compose pull
    
    log_success "Images pulled successfully"
}

# Build custom images
build_images() {
    log_info "Building custom Docker images..."
    
    # Build with appropriate target based on environment
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose build --target production
    else
        docker-compose build --target development
    fi
    
    log_success "Images built successfully"
}

# Deploy with Docker Compose
deploy_docker_compose() {
    log_info "Deploying with Docker Compose..."
    
    # Stop existing services
    docker-compose down --remove-orphans
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    check_service_health
    
    log_success "Docker Compose deployment completed"
}

# Deploy with Kubernetes
deploy_kubernetes() {
    log_info "Deploying with Kubernetes..."
    
    # Apply Kubernetes manifests
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/secrets.yaml
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    kubectl apply -f k8s/ingress.yaml
    
    # Wait for deployment to be ready
    kubectl rollout status deployment/frontier-ai -n frontier-ai
    
    log_success "Kubernetes deployment completed"
}

# Check service health
check_service_health() {
    log_info "Checking service health..."
    
    # Check API server
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_success "API server is healthy"
            break
        else
            log_warning "API server not ready (attempt $attempt/$max_attempts)"
            sleep 10
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "API server failed to become healthy"
        return 1
    fi
    
    # Check dashboard
    if curl -f http://localhost:8501 > /dev/null 2>&1; then
        log_success "Dashboard is healthy"
    else
        log_warning "Dashboard is not accessible"
    fi
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Wait for database to be ready
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec frontier-postgres pg_isready -U frontier > /dev/null 2>&1; then
            log_success "Database is ready"
            break
        else
            log_warning "Database not ready (attempt $attempt/$max_attempts)"
            sleep 5
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "Database failed to become ready"
        return 1
    fi
    
    # Run migrations
    docker exec frontier-api python -m alembic upgrade head
    
    log_success "Database migrations completed"
}

# Update configuration
update_configuration() {
    log_info "Updating configuration for $ENVIRONMENT environment..."
    
    # Copy environment-specific configuration
    if [ -f "$PROJECT_DIR/configs/$ENVIRONMENT.env" ]; then
        cp "$PROJECT_DIR/configs/$ENVIRONMENT.env" "$PROJECT_DIR/.env"
        log_success "Configuration updated for $ENVIRONMENT"
    else
        log_warning "No specific configuration found for $ENVIRONMENT, using default"
    fi
}

# Cleanup old resources
cleanup() {
    log_info "Cleaning up old resources..."
    
    # Remove unused Docker images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    # Remove unused networks
    docker network prune -f
    
    log_success "Cleanup completed"
}

# Rollback deployment
rollback() {
    log_info "Rolling back deployment..."
    
    # Find latest backup
    LATEST_BACKUP=$(ls -t "$PROJECT_DIR/backups" | head -n1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        log_error "No backup found for rollback"
        exit 1
    fi
    
    log_info "Rolling back to backup: $LATEST_BACKUP"
    
    # Stop current services
    docker-compose down
    
    # Restore configuration
    cp "$PROJECT_DIR/backups/$LATEST_BACKUP/.env" "$PROJECT_DIR/" 2>/dev/null || true
    
    # Restore database
    if [ -f "$PROJECT_DIR/backups/$LATEST_BACKUP/database_backup.sql" ]; then
        docker-compose up -d postgres
        sleep 10
        docker exec -i frontier-postgres psql -U frontier frontier_ai < "$PROJECT_DIR/backups/$LATEST_BACKUP/database_backup.sql"
    fi
    
    # Start services
    docker-compose up -d
    
    log_success "Rollback completed"
}

# Show deployment status
show_status() {
    log_info "Deployment Status:"
    echo ""
    
    # Docker Compose status
    if [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
        echo "Docker Compose Services:"
        docker-compose ps
        echo ""
    fi
    
    # Kubernetes status
    if command -v kubectl &> /dev/null; then
        echo "Kubernetes Resources:"
        kubectl get pods -n frontier-ai 2>/dev/null || true
        echo ""
    fi
    
    # Service health
    echo "Service Health:"
    curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "API server not accessible"
    echo ""
}

# Main deployment function
main() {
    log_info "Starting deployment for $ENVIRONMENT environment (version: $VERSION)"
    
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            backup_deployment
            update_configuration
            pull_images
            build_images
            
            if [ "$ENVIRONMENT" = "kubernetes" ]; then
                deploy_kubernetes
            else
                deploy_docker_compose
            fi
            
            run_migrations
            check_service_health
            cleanup
            show_status
            log_success "Deployment completed successfully!"
            ;;
        "rollback")
            rollback
            show_status
            ;;
        "status")
            show_status
            ;;
        "health")
            check_service_health
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|status|health} [environment] [version]"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy the application"
            echo "  rollback - Rollback to previous version"
            echo "  status   - Show deployment status"
            echo "  health   - Check service health"
            echo ""
            echo "Environments: development, staging, production, kubernetes"
            echo "Version: Docker image tag (default: latest)"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"










