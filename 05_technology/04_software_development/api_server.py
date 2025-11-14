#!/usr/bin/env python3
"""
REST API Server for Frontier AI Projects
Provides HTTP endpoints for brand analysis and model training.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# Add project paths
sys.path.append(str(Path(__file__).parent / "TruthGPT" / "brandkit"))
sys.path.append(str(Path(__file__).parent / "TruthGPT" / "Frontier-Model-run" / "scripts"))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from contextlib import asynccontextmanager

# Import our enhanced modules
from brand_analyzer import (
    BrandAnalyzerAPI, 
    AsyncBrandAnalyzer, 
    ProductionBrandAnalyzer,
    AutoTuningBrandAnalyzer,
    DistributedBrandAnalyzer
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global analyzer instances
analyzer_instances = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Frontier AI API Server...")
    
    # Initialize analyzers
    analyzer_instances['basic'] = BrandAnalyzerAPI()
    analyzer_instances['async'] = AsyncBrandAnalyzer()
    analyzer_instances['production'] = ProductionBrandAnalyzer()
    analyzer_instances['distributed'] = DistributedBrandAnalyzer(num_workers=4)
    
    # Initialize async analyzer
    await analyzer_instances['async'].initialize()
    analyzer_instances['production'].initialize()
    
    logger.info("All analyzers initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Frontier AI API Server...")
    if 'distributed' in analyzer_instances:
        analyzer_instances['distributed'].shutdown()
    logger.info("Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Frontier AI API",
    description="Advanced AI-powered brand analysis and model training API",
    version="2.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Pydantic models
class WebsiteData(BaseModel):
    colors: List[List[int]] = Field(..., description="RGB color values")
    typography: List[float] = Field(..., description="Typography features")
    layout: List[float] = Field(..., description="Layout features")
    text_features: List[float] = Field(..., description="Text embeddings")

class BatchAnalysisRequest(BaseModel):
    websites: List[WebsiteData] = Field(..., description="List of websites to analyze")
    use_cache: bool = Field(True, description="Whether to use caching")
    async_processing: bool = Field(False, description="Whether to use async processing")

class AnalysisResponse(BaseModel):
    success: bool
    brand_kit: Optional[Dict[str, Any]] = None
    consistency_score: Optional[float] = None
    analysis_time: Optional[float] = None
    error: Optional[str] = None
    monitoring: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    total_requests: int
    success_rate: float
    average_response_time: float
    memory_usage_gb: float
    cpu_usage_percent: float

class MetricsResponse(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    cache_hit_rate: float
    response_times: List[float]
    health_status: HealthResponse

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Frontier AI API Server",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "batch_analyze": "/batch_analyze",
            "metrics": "/metrics",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        health_status = analyzer_instances['production'].get_health_status()
        return HealthResponse(**health_status)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get detailed metrics."""
    try:
        metrics = analyzer_instances['production'].get_metrics()
        return MetricsResponse(**metrics)
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metrics retrieval failed: {str(e)}"
        )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_website(website_data: WebsiteData):
    """Analyze a single website."""
    try:
        start_time = time.time()
        
        # Convert to dict
        data_dict = website_data.dict()
        
        # Use production analyzer for monitoring
        result = analyzer_instances['production'].analyze_with_monitoring(data_dict)
        
        analysis_time = time.time() - start_time
        
        return AnalysisResponse(
            success=result['success'],
            brand_kit=result.get('brand_kit'),
            consistency_score=result.get('model_outputs', {}).get('consistency_score'),
            analysis_time=analysis_time,
            error=result.get('error'),
            monitoring=result.get('monitoring')
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@app.post("/analyze_async", response_model=AnalysisResponse)
async def analyze_website_async(website_data: WebsiteData):
    """Analyze a single website asynchronously."""
    try:
        start_time = time.time()
        
        # Convert to dict
        data_dict = website_data.dict()
        
        # Use async analyzer
        result = await analyzer_instances['async'].analyze_website_async(data_dict)
        
        analysis_time = time.time() - start_time
        
        return AnalysisResponse(
            success=result['success'],
            brand_kit=result.get('brand_kit'),
            consistency_score=result.get('model_outputs', {}).get('consistency_score'),
            analysis_time=analysis_time,
            error=result.get('error')
        )
        
    except Exception as e:
        logger.error(f"Async analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Async analysis failed: {str(e)}"
        )

@app.post("/batch_analyze", response_model=List[AnalysisResponse])
async def batch_analyze_websites(request: BatchAnalysisRequest):
    """Analyze multiple websites in batch."""
    try:
        start_time = time.time()
        
        # Convert to list of dicts
        websites = [website.dict() for website in request.websites]
        
        if request.async_processing:
            # Use async analyzer
            results = await analyzer_instances['async'].batch_analyze_async(websites)
        else:
            # Use basic analyzer
            results = analyzer_instances['basic'].batch_analyze(websites)
        
        analysis_time = time.time() - start_time
        
        # Convert results to response format
        response_results = []
        for result in results:
            response_results.append(AnalysisResponse(
                success=result['success'],
                brand_kit=result.get('brand_kit'),
                consistency_score=result.get('model_outputs', {}).get('consistency_score'),
                analysis_time=result.get('analysis_time', analysis_time / len(websites)),
                error=result.get('error')
            ))
        
        return response_results
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}"
        )

@app.post("/distributed_analyze", response_model=List[AnalysisResponse])
async def distributed_analyze_websites(request: BatchAnalysisRequest):
    """Analyze multiple websites using distributed processing."""
    try:
        start_time = time.time()
        
        # Convert to list of dicts
        websites = [website.dict() for website in request.websites]
        
        # Use distributed analyzer
        results = analyzer_instances['distributed'].analyze_distributed(websites)
        
        analysis_time = time.time() - start_time
        
        # Convert results to response format
        response_results = []
        for result in results:
            if result:  # Check if result is not None
                response_results.append(AnalysisResponse(
                    success=result['success'],
                    brand_kit=result.get('brand_kit'),
                    consistency_score=result.get('model_outputs', {}).get('consistency_score'),
                    analysis_time=result.get('analysis_time', analysis_time / len(websites)),
                    error=result.get('error')
                ))
            else:
                response_results.append(AnalysisResponse(
                    success=False,
                    error="Distributed processing failed",
                    analysis_time=analysis_time / len(websites)
                ))
        
        return response_results
        
    except Exception as e:
        logger.error(f"Distributed analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Distributed analysis failed: {str(e)}"
        )

@app.get("/cache_stats")
async def get_cache_stats():
    """Get cache statistics for async analyzer."""
    try:
        stats = analyzer_instances['async'].get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"Cache stats retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache stats retrieval failed: {str(e)}"
        )

@app.post("/clear_cache")
async def clear_cache():
    """Clear all caches."""
    try:
        # Clear async analyzer cache
        analyzer_instances['async'].memory_manager.clear_cache()
        
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache clear failed: {str(e)}"
        )

# Training endpoints (placeholder for future implementation)
@app.post("/train_model")
async def train_model(config: Dict[str, Any]):
    """Train a new model (placeholder)."""
    return {"message": "Training endpoint not yet implemented", "config": config}

@app.get("/training_status/{job_id}")
async def get_training_status(job_id: str):
    """Get training status (placeholder)."""
    return {"job_id": job_id, "status": "not_implemented"}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": time.time()
        }
    )

# Main function
def main():
    """Main function to run the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Frontier AI API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    
    args = parser.parse_args()
    
    logger.info(f"Starting Frontier AI API Server on {args.host}:{args.port}")
    
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        workers=args.workers,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()










