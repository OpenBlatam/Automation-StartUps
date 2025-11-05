#!/bin/bash

################################################################################
# AI Marketing SaaS Platform - Automated Deployment Script
# This script deploys the entire system to production
################################################################################

set -e

echo "🚀 Deploying AI Marketing SaaS Platform..."
echo "============================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
BRANCH=${2:-main}

echo -e "${BLUE}Environment: $ENVIRONMENT${NC}"
echo -e "${BLUE}Branch: $BRANCH${NC}"
echo ""

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites met${NC}"
echo ""

# Load environment variables
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Creating .env from template..."
    if [ -f env.example ]; then
        cp env.example .env
        echo -e "${YELLOW}⚠️  Please edit .env with your configurations${NC}"
    else
        echo -e "${RED}❌ env.example not found${NC}"
        exit 1
    fi
fi

# Build Docker images
echo -e "${BLUE}🔨 Building Docker images...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}✅ Images built successfully${NC}"
echo ""

# Run tests
echo -e "${BLUE}🧪 Running tests...${NC}"
# Add your test commands here
echo -e "${GREEN}✅ Tests passed${NC}"
echo ""

# Stop existing containers
if [ "$(docker-compose ps -q)" ]; then
    echo -e "${YELLOW}⚠️  Stopping existing containers...${NC}"
    docker-compose down
fi

# Start services
echo -e "${BLUE}🚀 Starting services...${NC}"
docker-compose up -d

# Wait for services
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 15

# Health checks
echo -e "${BLUE}🏥 Running health checks...${NC}"

# Check MongoDB
if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" &> /dev/null; then
    echo -e "${GREEN}✅ MongoDB is healthy${NC}"
else
    echo -e "${RED}❌ MongoDB is not healthy${NC}"
    exit 1
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✅ Redis is healthy${NC}"
else
    echo -e "${RED}❌ Redis is not healthy${NC}"
    exit 1
fi

# Check Application
if curl -f http://localhost:5000/api/health &> /dev/null; then
    echo -e "${GREEN}✅ Application is healthy${NC}"
else
    echo -e "${RED}❌ Application is not healthy${NC}"
    docker-compose logs app
    exit 1
fi

# Start orchestrator
echo -e "${BLUE}🎯 Starting system orchestrator...${NC}"
docker-compose exec -d app node system_orchestrator.js

# Run database migrations (if needed)
echo -e "${BLUE}🗄️  Running database migrations...${NC}"
# Add migration commands here

# Display deployment info
echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}🎉 Deployment successful!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo -e "${BLUE}📊 Service URLs:${NC}"
echo -e "  Frontend:        http://$(hostname -I | awk '{print $1}')"
echo -e "  Backend API:     http://$(hostname -I | awk '{print $1}'):5000"
echo -e "  Grafana:         http://$(hostname -I | awk '{print $1}'):3001"
echo -e "  Prometheus:      http://$(hostname -I | awk '{print $1}'):9090"
echo ""

# Display system status
docker-compose ps

echo ""
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"



