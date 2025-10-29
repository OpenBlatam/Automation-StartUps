#!/bin/bash

################################################################################
# AI Marketing SaaS Platform - Automated Startup Script
# This script starts the entire system autonomously
################################################################################

set -e

echo "🚀 Starting AI Marketing SaaS Platform..."
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    echo -e "${GREEN}✅ Loading environment variables...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠️  No .env file found. Using defaults.${NC}"
fi

# Create necessary directories
echo -e "${BLUE}📁 Creating necessary directories...${NC}"
mkdir -p logs uploads monitoring/prometheus monitoring/grafana/dashboards monitoring/grafana/datasources

# Check if system is already running
if [ "$(docker-compose ps -q)" ]; then
    echo -e "${YELLOW}⚠️  System is already running. Restarting...${NC}"
    docker-compose down
fi

# Start Docker containers
echo -e "${GREEN}🐳 Starting Docker containers...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check service health
check_service() {
    local service=$1
    local port=$2
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T $service echo "OK" &> /dev/null; then
            echo -e "${GREEN}✅ $service is healthy${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        echo "Waiting for $service... ($attempt/$max_attempts)"
        sleep 2
    done
    
    echo -e "${RED}❌ $service failed to start${NC}"
    return 1
}

# Check MongoDB
check_service mongodb 27017 || exit 1

# Check Redis
check_service redis 6379 || exit 1

# Check App
echo -e "${BLUE}🔍 Checking application health...${NC}"
for i in {1..30}; do
    if curl -f http://localhost:5000/api/health &> /dev/null; then
        echo -e "${GREEN}✅ Application is healthy${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Application failed to start${NC}"
        docker-compose logs app
        exit 1
    fi
    sleep 2
done

# Start ultimate system integration
echo -e "${BLUE}🌟 Starting ULTIMATE system integration...${NC}"
docker-compose exec -d app node ULTIMATE_SYSTEM_INTEGRATION.js

# Display status
echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}🎉 System started successfully!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo -e "${BLUE}📊 Service URLs:${NC}"
echo -e "  Frontend:        http://localhost"
echo -e "  Backend API:     http://localhost:5000"
echo -e "  API Health:      http://localhost:5000/api/health"
echo -e "  Grafana:         http://localhost:3001"
echo -e "  Prometheus:      http://localhost:9090"
echo ""
echo -e "${BLUE}📝 View logs:${NC}"
echo -e "  docker-compose logs -f"
echo ""
echo -e "${BLUE}🛑 Stop system:${NC}"
echo -e "  docker-compose down"
echo ""

# Display running containers
docker-compose ps

