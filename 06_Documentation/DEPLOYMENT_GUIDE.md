# 🚀 IA Marketing SaaS - Deployment Guide

## Complete Setup and Deployment Instructions

This guide will help you deploy the IA Marketing SaaS platform from scratch to production.

---

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: Minimum 50GB free space
- **CPU**: 4+ cores recommended

### Software Requirements
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Node.js**: 18.0+ (for development)
- **Git**: Latest version

### API Keys Required
- **OpenAI API Key**: For GPT-4 and DALL-E
- **Google AI Key**: For Gemini models
- **Anthropic API Key**: For Claude models
- **Stripe Secret Key**: For payments
- **SendGrid API Key**: For email services

---

## 🚀 Quick Start (5 Minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/ia-marketing/saas-platform.git
cd saas-platform
```

### 2. Configure Environment
```bash
# Copy environment template
cp env.example .env

# Edit with your API keys
nano .env
```

### 3. Deploy with Docker
```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Deploy all services
./scripts/deploy.sh
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:3001
- **API Documentation**: http://localhost:3001/api/docs
- **Grafana Dashboard**: http://localhost:3003 (admin/admin123)

---

## 🔧 Detailed Setup

### Environment Configuration

Edit the `.env` file with your configuration:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/ia_marketing
REDIS_URL=redis://:redis123@redis:6379

# AI Services
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_AI_KEY=your-google-ai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# External Services
STRIPE_SECRET_KEY=sk_test_your-stripe-key-here
SENDGRID_API_KEY=SG.your-sendgrid-key-here

# Security
JWT_SECRET=your-super-secret-jwt-key-minimum-32-characters
```

### Database Setup

The platform uses PostgreSQL with Redis for caching:

```bash
# Database will be automatically created
# Run migrations
docker-compose exec backend npm run migrate

# Seed initial data
docker-compose exec backend npm run seed
```

### AI Services Configuration

#### OpenAI Setup
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add to `.env` file
4. Ensure you have credits in your account

#### Google AI Setup
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Add to `.env` file

#### Anthropic Setup
1. Go to https://console.anthropic.com/
2. Create a new API key
3. Add to `.env` file

---

## 🐳 Docker Deployment

### Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Environment

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale backend=3 --scale ai-worker=2
```

### Service Management

```bash
# Check status
./scripts/deploy.sh status

# Restart services
./scripts/deploy.sh restart

# View logs
./scripts/deploy.sh logs

# Update services
./scripts/deploy.sh update
```

---

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS

1. **Create ECS Cluster**
```bash
aws ecs create-cluster --cluster-name ia-marketing-cluster
```

2. **Create Task Definition**
```json
{
  "family": "ia-marketing-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole"
}
```

3. **Deploy Services**
```bash
# Create ECS service
aws ecs create-service \
  --cluster ia-marketing-cluster \
  --service-name ia-marketing-service \
  --task-definition ia-marketing-task \
  --desired-count 2
```

#### Using AWS EKS

1. **Create EKS Cluster**
```bash
eksctl create cluster --name ia-marketing-cluster --region us-west-2
```

2. **Deploy with Helm**
```bash
# Install Helm chart
helm install ia-marketing ./helm/ia-marketing \
  --set image.tag=latest \
  --set ingress.enabled=true
```

### Google Cloud Platform

#### Using Google Kubernetes Engine

1. **Create GKE Cluster**
```bash
gcloud container clusters create ia-marketing-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-standard-4
```

2. **Deploy Application**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Expose services
kubectl expose deployment frontend --type=LoadBalancer --port=80
```

### Azure Deployment

#### Using Azure Container Instances

1. **Create Resource Group**
```bash
az group create --name ia-marketing-rg --location eastus
```

2. **Deploy Container Group**
```bash
az container create \
  --resource-group ia-marketing-rg \
  --name ia-marketing-app \
  --image ia-marketing/frontend:latest \
  --dns-name-label ia-marketing-app \
  --ports 80
```

---

## 🔒 Security Configuration

### SSL/TLS Setup

#### Using Let's Encrypt

```bash
# Install Certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com

# Update nginx configuration
cp nginx/nginx-ssl.conf nginx/nginx.conf
```

#### Using Cloudflare

1. Add your domain to Cloudflare
2. Enable SSL/TLS encryption
3. Configure DNS records
4. Enable security features

### Database Security

```bash
# Enable SSL for PostgreSQL
docker-compose exec postgres psql -U postgres -c "ALTER SYSTEM SET ssl = on;"

# Create read-only user
docker-compose exec postgres psql -U postgres -c "CREATE USER readonly WITH PASSWORD 'readonly123';"
```

### API Security

```bash
# Enable rate limiting
export RATE_LIMIT_ENABLED=true
export RATE_LIMIT_MAX=1000

# Enable CORS
export CORS_ORIGIN=https://yourdomain.com

# Enable Helmet security headers
export HELMET_ENABLED=true
```

---

## 📊 Monitoring and Logging

### Prometheus Setup

```bash
# Access Prometheus
open http://localhost:9090

# Configure alerts
cp monitoring/alerts.yml monitoring/prometheus/alerts/
```

### Grafana Dashboard

```bash
# Access Grafana
open http://localhost:3003

# Login: admin/admin123
# Import dashboards from monitoring/grafana/dashboards/
```

### Application Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ai-worker
```

### Health Checks

```bash
# Check service health
curl http://localhost:3001/health

# Check database
docker-compose exec postgres pg_isready

# Check Redis
docker-compose exec redis redis-cli ping
```

---

## 🔄 Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres ia_marketing > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U postgres ia_marketing < backup.sql
```

### File Backup

```bash
# Backup uploads
tar -czf uploads-backup.tar.gz server/uploads/

# Restore uploads
tar -xzf uploads-backup.tar.gz
```

### Automated Backups

```bash
# Setup cron job for daily backups
0 2 * * * /path/to/scripts/backup.sh
```

---

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :3000
lsof -i :3001

# Kill process
kill -9 PID
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### AI Service Issues
```bash
# Check API keys
docker-compose exec backend node -e "console.log(process.env.OPENAI_API_KEY)"

# Test AI connection
docker-compose exec backend npm run test:ai
```

#### Memory Issues
```bash
# Increase Docker memory limit
# In Docker Desktop: Settings > Resources > Memory

# Or use swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Performance Optimization

#### Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_content_type ON content(type);
CREATE INDEX idx_analytics_date ON analytics(created_at);
```

#### Redis Optimization
```bash
# Configure Redis memory
echo "maxmemory 1gb" >> redis.conf
echo "maxmemory-policy allkeys-lru" >> redis.conf
```

#### Application Optimization
```bash
# Enable gzip compression
export COMPRESSION_ENABLED=true

# Enable caching
export CACHE_ENABLED=true
export CACHE_TTL=3600
```

---

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Scale AI workers
docker-compose up -d --scale ai-worker=5

# Use load balancer
docker-compose up -d nginx
```

### Vertical Scaling

```bash
# Increase memory limits
docker-compose up -d --scale backend=1 -e NODE_OPTIONS="--max-old-space-size=4096"
```

### Database Scaling

```bash
# Use read replicas
docker-compose up -d postgres-replica

# Configure connection pooling
export DATABASE_POOL_SIZE=20
```

---

## 🔄 Updates and Maintenance

### Application Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d

# Run migrations
docker-compose exec backend npm run migrate
```

### Security Updates

```bash
# Update base images
docker-compose pull

# Scan for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image ia-marketing/backend:latest
```

### Monitoring Updates

```bash
# Update monitoring stack
docker-compose pull prometheus grafana

# Restart monitoring
docker-compose restart prometheus grafana
```

---

## 📞 Support

### Getting Help

- **Documentation**: https://docs.ia-marketing.com
- **Community**: https://community.ia-marketing.com
- **Support Email**: support@ia-marketing.com
- **Discord**: https://discord.gg/ia-marketing

### Reporting Issues

1. Check existing issues: https://github.com/ia-marketing/saas-platform/issues
2. Create new issue with:
   - System information
   - Error logs
   - Steps to reproduce
   - Expected behavior

### Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

---

## 🎯 Next Steps

After successful deployment:

1. **Configure Domain**: Point your domain to the server
2. **Setup SSL**: Enable HTTPS for security
3. **Configure Monitoring**: Set up alerts and dashboards
4. **Create Users**: Add team members and set permissions
5. **Import Data**: Migrate existing marketing data
6. **Test Features**: Verify all AI features work correctly
7. **Go Live**: Start using the platform for your marketing

---

**🎉 Congratulations! Your IA Marketing SaaS platform is now deployed and ready to revolutionize your marketing!**

