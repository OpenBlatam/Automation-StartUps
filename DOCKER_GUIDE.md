# Docker Guide for Ultimate Launch Planning System

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- PowerShell (for Windows) or Bash (for Linux/Mac)

### Basic Commands

```powershell
# Build and start all services
.\docker-run.ps1 -Action build
.\docker-run.ps1 -Action up

# Check health status
.\docker-run.ps1 -Action health

# View logs
.\docker-run.ps1 -Action logs

# Stop services
.\docker-run.ps1 -Action down
```

## Service Architecture

The system runs with three main services:

### 1. Launch Planning API (`launch-planning-api`)
- **Port**: 8000
- **Purpose**: Core API service
- **Health Check**: `http://localhost:8000/health`
- **Command**: `python launch_planning_api.py`

### 2. Launch Planning Dashboard (`launch-planning-dashboard`)
- **Port**: 8501
- **Purpose**: Streamlit web dashboard
- **URL**: `http://localhost:8501`
- **Command**: `python launch_planning_dashboard.py`

### 3. Launch Planning Demo (`launch-planning-demo`)
- **Purpose**: Runs the complete demo
- **Command**: `python ultimate_launch_demo.py`
- **Note**: Runs once and exits

## Advanced Usage

### Service-Specific Operations

```powershell
# Start only the API service
.\docker-run.ps1 -Action up -Service launch-planning-api

# View logs for specific service
.\docker-run.ps1 -Action logs -Service launch-planning-dashboard

# Open shell in API container
.\docker-run.ps1 -Action shell -Service launch-planning-api

# Run services in foreground (see real-time logs)
.\docker-run.ps1 -Action up -Detach:$false
```

### Development Mode

```powershell
# Build with no cache
docker-compose build --no-cache

# Run with volume mounts for development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production Deployment

```powershell
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production settings
docker-compose -f docker-compose.prod.yml up -d
```

## Health Monitoring

### Health Check Endpoints

- **API Health**: `http://localhost:8000/health`
- **Dashboard Health**: `http://localhost:8501/_stcore/health`

### Manual Health Check

```powershell
# Run comprehensive health check
.\docker-run.ps1 -Action health

# Check specific service status
docker-compose ps launch-planning-api
```

## Logging

### View Logs

```powershell
# All services
.\docker-run.ps1 -Action logs

# Specific service
.\docker-run.ps1 -Action logs -Service launch-planning-api

# Follow logs in real-time
docker-compose logs -f
```

### Log Files

Logs are stored in:
- Container: `/app/logs/`
- Host: `./logs/` (mounted volume)

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```powershell
   # Check what's using the port
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID <PID> /F
   ```

2. **Docker Not Running**
   ```powershell
   # Start Docker Desktop
   # Or restart Docker service
   Restart-Service docker
   ```

3. **Permission Issues**
   ```powershell
   # Run PowerShell as Administrator
   # Or adjust Docker Desktop settings
   ```

4. **Out of Disk Space**
   ```powershell
   # Clean up Docker resources
   .\docker-run.ps1 -Action clean -Force
   ```

### Debug Mode

```powershell
# Run with debug logging
$env:LOG_LEVEL="DEBUG"
.\docker-run.ps1 -Action up

# Check container logs
docker-compose logs launch-planning-api
```

## Environment Variables

### Available Variables

- `ENVIRONMENT`: `production`, `development`, `demo`
- `LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `API_HOST`: API host address (default: `0.0.0.0`)
- `API_PORT`: API port (default: `8000`)

### Setting Variables

```powershell
# In docker-compose.yml
environment:
  - ENVIRONMENT=production
  - LOG_LEVEL=INFO

# Or via .env file
echo "ENVIRONMENT=production" > .env
echo "LOG_LEVEL=INFO" >> .env
```

## Data Persistence

### Volumes

- `./data:/app/data` - Application data
- `./logs:/app/logs` - Log files

### Backup Data

```powershell
# Backup data directory
docker run --rm -v ${PWD}/data:/backup -v ${PWD}:/data alpine tar czf /backup/data-backup.tar.gz -C /data data

# Restore data
docker run --rm -v ${PWD}/data:/backup -v ${PWD}:/data alpine tar xzf /backup/data-backup.tar.gz -C /data
```

## Security

### Best Practices

1. **Use non-root user** (already configured)
2. **Limit container resources**
3. **Use secrets for sensitive data**
4. **Regular security updates**

### Resource Limits

```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

## Scaling

### Horizontal Scaling

```powershell
# Scale API service
docker-compose up -d --scale launch-planning-api=3

# Use load balancer
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

## Monitoring

### Container Metrics

```powershell
# View container stats
docker stats

# Check resource usage
docker-compose top
```

### Application Metrics

- Access dashboard at `http://localhost:8501`
- View API metrics at `http://localhost:8000/metrics`
- Check health at `http://localhost:8000/health`

## Cleanup

### Remove Everything

```powershell
# Stop and remove all resources
.\docker-run.ps1 -Action clean -Force

# Or manually
docker-compose down -v --remove-orphans
docker system prune -a -f
```

### Selective Cleanup

```powershell
# Remove only containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Support

For issues or questions:
1. Check logs: `.\docker-run.ps1 -Action logs`
2. Check health: `.\docker-run.ps1 -Action health`
3. Review this guide
4. Check Docker Desktop logs
5. Restart Docker Desktop if needed







