# Docker Management Script for Ultimate Launch Planning System
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("build", "up", "down", "logs", "shell", "health", "clean")]
    [string]$Action = "up",
    
    [Parameter(Mandatory=$false)]
    [string]$Service = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Detach = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host "Docker Management Script for Ultimate Launch Planning System" -ForegroundColor Cyan
    Write-Host "Usage: .\docker-run.ps1 -Action <action> [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Green
    Write-Host "  build    - Build Docker images"
    Write-Host "  up       - Start services (default)"
    Write-Host "  down     - Stop services"
    Write-Host "  logs     - Show logs"
    Write-Host "  shell    - Open shell in container"
    Write-Host "  health   - Check health status"
    Write-Host "  clean    - Clean up containers and images"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Green
    Write-Host "  -Service <name>  - Target specific service"
    Write-Host "  -Detach          - Run in background (default: true)"
    Write-Host "  -Force           - Force action without confirmation"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\docker-run.ps1 -Action build"
    Write-Host "  .\docker-run.ps1 -Action up -Service launch-planning-api"
    Write-Host "  .\docker-run.ps1 -Action logs -Service launch-planning-dashboard"
    Write-Host "  .\docker-run.ps1 -Action shell -Service launch-planning-api"
    Write-Host "  .\docker-run.ps1 -Action health"
    Write-Host "  .\docker-run.ps1 -Action clean -Force"
}

function Test-Docker {
    Write-Host "Checking Docker installation..." -ForegroundColor Cyan
    try {
        $dockerVersion = docker --version
        Write-Host "Docker found: $dockerVersion" -ForegroundColor Green
        
        $dockerComposeVersion = docker-compose --version
        Write-Host "Docker Compose found: $dockerComposeVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Docker not found. Please install Docker Desktop." -ForegroundColor Red
        Write-Host "Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        return $false
    }
}

function Build-Images {
    Write-Host "Building Docker images..." -ForegroundColor Cyan
    docker-compose build
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Images built successfully!" -ForegroundColor Green
    } else {
        throw "Failed to build images"
    }
}

function Start-Services {
    param([string]$ServiceName = "")
    
    Write-Host "Starting services..." -ForegroundColor Cyan
    
    if ($ServiceName) {
        if ($Detach) {
            docker-compose up -d $ServiceName
        } else {
            docker-compose up $ServiceName
        }
    } else {
        if ($Detach) {
            docker-compose up -d
        } else {
            docker-compose up
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Services started successfully!" -ForegroundColor Green
        if ($Detach) {
            Write-Host "Services running in background. Use '.\docker-run.ps1 -Action logs' to view logs." -ForegroundColor Yellow
        }
    } else {
        throw "Failed to start services"
    }
}

function Stop-Services {
    Write-Host "Stopping services..." -ForegroundColor Cyan
    docker-compose down
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Services stopped successfully!" -ForegroundColor Green
    } else {
        throw "Failed to stop services"
    }
}

function Show-Logs {
    param([string]$ServiceName = "")
    
    if ($ServiceName) {
        Write-Host "Showing logs for service: $ServiceName" -ForegroundColor Cyan
        docker-compose logs -f $ServiceName
    } else {
        Write-Host "Showing logs for all services..." -ForegroundColor Cyan
        docker-compose logs -f
    }
}

function Open-Shell {
    param([string]$ServiceName = "launch-planning-api")
    
    Write-Host "Opening shell in service: $ServiceName" -ForegroundColor Cyan
    docker-compose exec $ServiceName /bin/bash
}

function Check-Health {
    Write-Host "Checking health status..." -ForegroundColor Cyan
    
    # Check if services are running
    $services = docker-compose ps --services
    foreach ($service in $services) {
        $status = docker-compose ps $service --format "table {{.State}}"
        Write-Host "$service`: $status" -ForegroundColor Yellow
    }
    
    # Try to access health endpoint
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
        Write-Host "Health endpoint accessible: $($response.StatusCode)" -ForegroundColor Green
    }
    catch {
        Write-Host "Health endpoint not accessible: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Clean-Up {
    if (-not $Force) {
        $confirmation = Read-Host "This will remove all containers, images, and volumes. Continue? (y/N)"
        if ($confirmation -ne "y" -and $confirmation -ne "Y") {
            Write-Host "Cleanup cancelled." -ForegroundColor Yellow
            return
        }
    }
    
    Write-Host "Cleaning up Docker resources..." -ForegroundColor Cyan
    
    # Stop and remove containers
    docker-compose down -v --remove-orphans
    
    # Remove images
    docker-compose down --rmi all
    
    # Clean up unused resources
    docker system prune -f
    
    Write-Host "Cleanup completed!" -ForegroundColor Green
}

# Main execution
try {
    if (-not (Test-Docker)) {
        exit 1
    }
    
    switch ($Action) {
        "build" {
            Build-Images
        }
        "up" {
            Start-Services -ServiceName $Service
        }
        "down" {
            Stop-Services
        }
        "logs" {
            Show-Logs -ServiceName $Service
        }
        "shell" {
            Open-Shell -ServiceName $Service
        }
        "health" {
            Check-Health
        }
        "clean" {
            Clean-Up
        }
        default {
            Show-Help
        }
    }
}
catch {
    Write-Error "Error: $($_.Exception.Message)"
    Write-Host "Use '.\docker-run.ps1 -Action help' for usage information." -ForegroundColor Yellow
    exit 1
}








