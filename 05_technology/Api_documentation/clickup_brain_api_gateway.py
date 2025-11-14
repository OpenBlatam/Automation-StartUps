#!/usr/bin/env python3
"""
ClickUp Brain API Gateway
========================

High-performance API gateway with rate limiting, authentication, routing,
load balancing, and request/response transformation.
"""

import asyncio
import json
import time
import hashlib
import hmac
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
import jwt
from collections import defaultdict, deque
import aiohttp
from aiohttp import web, ClientSession, ClientTimeout
import yaml

ROOT = Path(__file__).parent

@dataclass
class RateLimit:
    """Rate limiting configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    window_size: int = 60  # seconds

@dataclass
class AuthenticationConfig:
    """Authentication configuration."""
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiry: int = 3600  # seconds
    api_key_header: str = "X-API-Key"
    api_keys: Dict[str, str] = field(default_factory=dict)
    require_auth: bool = True

@dataclass
class RouteConfig:
    """Route configuration."""
    path: str
    target_url: str
    methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    rate_limit: Optional[RateLimit] = None
    auth_required: bool = True
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    headers: Dict[str, str] = field(default_factory=dict)
    transform_request: Optional[Callable] = None
    transform_response: Optional[Callable] = None

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration."""
    strategy: str = "round_robin"  # round_robin, least_connections, weighted
    health_check_interval: int = 30
    health_check_timeout: int = 5
    max_retries: int = 3

class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, rate_limit: RateLimit):
        self.rate_limit = rate_limit
        self.buckets: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client."""
        async with self._lock:
            now = time.time()
            
            if client_id not in self.buckets:
                self.buckets[client_id] = {
                    'tokens': self.rate_limit.burst_limit,
                    'last_refill': now,
                    'requests': deque(maxlen=self.rate_limit.requests_per_minute)
                }
            
            bucket = self.buckets[client_id]
            
            # Refill tokens based on time passed
            time_passed = now - bucket['last_refill']
            tokens_to_add = time_passed * (self.rate_limit.requests_per_minute / 60)
            bucket['tokens'] = min(self.rate_limit.burst_limit, bucket['tokens'] + tokens_to_add)
            bucket['last_refill'] = now
            
            # Check if we have tokens available
            if bucket['tokens'] >= 1:
                bucket['tokens'] -= 1
                bucket['requests'].append(now)
                return True
            
            return False
    
    async def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        async with self._lock:
            if client_id not in self.buckets:
                return self.rate_limit.requests_per_minute
            
            bucket = self.buckets[client_id]
            now = time.time()
            
            # Count requests in the last minute
            cutoff = now - 60
            recent_requests = sum(1 for req_time in bucket['requests'] if req_time > cutoff)
            
            return max(0, self.rate_limit.requests_per_minute - recent_requests)

class AuthenticationManager:
    """Handles authentication and authorization."""
    
    def __init__(self, config: AuthenticationConfig):
        self.config = config
        self.logger = logging.getLogger("auth_manager")
    
    def generate_jwt_token(self, user_id: str, roles: List[str] = None) -> str:
        """Generate JWT token for user."""
        payload = {
            'user_id': user_id,
            'roles': roles or [],
            'exp': datetime.utcnow() + timedelta(seconds=self.config.jwt_expiry),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.config.jwt_secret, algorithm=self.config.jwt_algorithm)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, self.config.jwt_secret, algorithms=[self.config.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid JWT token")
            return None
    
    def verify_api_key(self, api_key: str) -> bool:
        """Verify API key."""
        return api_key in self.config.api_keys
    
    async def authenticate_request(self, request: web.Request) -> Optional[Dict[str, Any]]:
        """Authenticate incoming request."""
        # Check for JWT token
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            payload = self.verify_jwt_token(token)
            if payload:
                return payload
        
        # Check for API key
        api_key = request.headers.get(self.config.api_key_header)
        if api_key and self.verify_api_key(api_key):
            return {'user_id': 'api_user', 'roles': ['api']}
        
        return None

class LoadBalancer:
    """Load balancer for distributing requests."""
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.targets: List[str] = []
        self.target_health: Dict[str, bool] = {}
        self.target_connections: Dict[str, int] = {}
        self.current_index = 0
        self._lock = asyncio.Lock()
    
    def add_target(self, target_url: str) -> None:
        """Add a target to the load balancer."""
        self.targets.append(target_url)
        self.target_health[target_url] = True
        self.target_connections[target_url] = 0
    
    def remove_target(self, target_url: str) -> None:
        """Remove a target from the load balancer."""
        if target_url in self.targets:
            self.targets.remove(target_url)
            self.target_health.pop(target_url, None)
            self.target_connections.pop(target_url, None)
    
    async def get_target(self) -> Optional[str]:
        """Get the next target based on load balancing strategy."""
        if not self.targets:
            return None
        
        healthy_targets = [t for t in self.targets if self.target_health.get(t, False)]
        if not healthy_targets:
            return None
        
        async with self._lock:
            if self.config.strategy == "round_robin":
                target = healthy_targets[self.current_index % len(healthy_targets)]
                self.current_index += 1
                return target
            
            elif self.config.strategy == "least_connections":
                target = min(healthy_targets, key=lambda t: self.target_connections.get(t, 0))
                return target
            
            else:  # weighted (simplified)
                return healthy_targets[0]
    
    async def mark_connection_start(self, target: str) -> None:
        """Mark the start of a connection to a target."""
        async with self._lock:
            self.target_connections[target] = self.target_connections.get(target, 0) + 1
    
    async def mark_connection_end(self, target: str) -> None:
        """Mark the end of a connection to a target."""
        async with self._lock:
            self.target_connections[target] = max(0, self.target_connections.get(target, 0) - 1)
    
    async def health_check(self, target: str) -> bool:
        """Perform health check on a target."""
        try:
            timeout = ClientTimeout(total=self.config.health_check_timeout)
            async with ClientSession(timeout=timeout) as session:
                async with session.get(f"{target}/health") as response:
                    is_healthy = response.status == 200
                    self.target_health[target] = is_healthy
                    return is_healthy
        except Exception:
            self.target_health[target] = False
            return False
    
    async def start_health_checks(self) -> None:
        """Start periodic health checks."""
        while True:
            for target in self.targets:
                await self.health_check(target)
            await asyncio.sleep(self.config.health_check_interval)

class APIGateway:
    """Main API Gateway implementation."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or ROOT / "gateway_config.yaml"
        self.routes: Dict[str, RouteConfig] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.load_balancers: Dict[str, LoadBalancer] = {}
        self.auth_manager: Optional[AuthenticationManager] = None
        self.logger = logging.getLogger("api_gateway")
        self.metrics: Dict[str, Any] = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'requests_rate_limited': 0,
            'requests_auth_failed': 0
        }
        
        self._load_config()
    
    def _load_config(self) -> None:
        """Load gateway configuration."""
        if not self.config_path.exists():
            self._create_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Load authentication config
            auth_config = AuthenticationConfig(**config.get('authentication', {}))
            self.auth_manager = AuthenticationManager(auth_config)
            
            # Load routes
            for route_data in config.get('routes', []):
                route = RouteConfig(**route_data)
                self.routes[route.path] = route
                
                # Create rate limiter if configured
                if route.rate_limit:
                    self.rate_limiters[route.path] = RateLimiter(route.rate_limit)
                
                # Create load balancer if multiple targets
                if isinstance(route.target_url, list):
                    lb_config = LoadBalancerConfig(**config.get('load_balancer', {}))
                    load_balancer = LoadBalancer(lb_config)
                    for target in route.target_url:
                        load_balancer.add_target(target)
                    self.load_balancers[route.path] = load_balancer
            
            self.logger.info(f"Loaded {len(self.routes)} routes")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default configuration file."""
        default_config = {
            'authentication': {
                'jwt_secret': 'your-secret-key-change-in-production',
                'jwt_algorithm': 'HS256',
                'jwt_expiry': 3600,
                'api_key_header': 'X-API-Key',
                'api_keys': {
                    'demo-key': 'demo-secret'
                },
                'require_auth': True
            },
            'routes': [
                {
                    'path': '/api/v1/tasks',
                    'target_url': 'http://localhost:8001',
                    'methods': ['GET', 'POST', 'PUT', 'DELETE'],
                    'rate_limit': {
                        'requests_per_minute': 60,
                        'requests_per_hour': 1000,
                        'burst_limit': 10
                    },
                    'auth_required': True,
                    'timeout': 30
                }
            ],
            'load_balancer': {
                'strategy': 'round_robin',
                'health_check_interval': 30,
                'health_check_timeout': 5,
                'max_retries': 3
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        self.logger.info(f"Created default configuration at {self.config_path}")
    
    async def handle_request(self, request: web.Request) -> web.Response:
        """Handle incoming request through the gateway."""
        start_time = time.time()
        self.metrics['requests_total'] += 1
        
        try:
            # Find matching route
            route = self._find_route(request.path)
            if not route:
                return web.json_response(
                    {'error': 'Route not found'}, 
                    status=404
                )
            
            # Check if method is allowed
            if request.method not in route.methods:
                return web.json_response(
                    {'error': 'Method not allowed'}, 
                    status=405
                )
            
            # Rate limiting
            if route.path in self.rate_limiters:
                client_id = self._get_client_id(request)
                rate_limiter = self.rate_limiters[route.path]
                
                if not await rate_limiter.is_allowed(client_id):
                    self.metrics['requests_rate_limited'] += 1
                    return web.json_response(
                        {'error': 'Rate limit exceeded'}, 
                        status=429
                    )
            
            # Authentication
            if route.auth_required and self.auth_manager:
                auth_result = await self.auth_manager.authenticate_request(request)
                if not auth_result:
                    self.metrics['requests_auth_failed'] += 1
                    return web.json_response(
                        {'error': 'Authentication required'}, 
                        status=401
                    )
            
            # Get target URL
            target_url = await self._get_target_url(route, request)
            if not target_url:
                return web.json_response(
                    {'error': 'No healthy targets available'}, 
                    status=503
                )
            
            # Forward request
            response = await self._forward_request(request, target_url, route)
            
            # Update metrics
            duration = time.time() - start_time
            if response.status < 400:
                self.metrics['requests_success'] += 1
            else:
                self.metrics['requests_failed'] += 1
            
            # Add gateway headers
            response.headers['X-Gateway-Time'] = str(duration)
            response.headers['X-Gateway-Target'] = target_url
            
            return response
            
        except Exception as e:
            self.metrics['requests_failed'] += 1
            self.logger.error(f"Error handling request: {e}")
            return web.json_response(
                {'error': 'Internal gateway error'}, 
                status=500
            )
    
    def _find_route(self, path: str) -> Optional[RouteConfig]:
        """Find matching route for path."""
        # Simple exact match - can be extended with pattern matching
        return self.routes.get(path)
    
    def _get_client_id(self, request: web.Request) -> str:
        """Get client identifier for rate limiting."""
        # Use IP address as client ID
        return request.remote
    
    async def _get_target_url(self, route: RouteConfig, request: web.Request) -> Optional[str]:
        """Get target URL for request."""
        if isinstance(route.target_url, list):
            # Use load balancer
            if route.path in self.load_balancers:
                load_balancer = self.load_balancers[route.path]
                return await load_balancer.get_target()
            else:
                return route.target_url[0] if route.target_url else None
        else:
            return route.target_url
    
    async def _forward_request(self, request: web.Request, target_url: str, route: RouteConfig) -> web.Response:
        """Forward request to target service."""
        # Prepare request data
        request_data = {
            'method': request.method,
            'url': f"{target_url}{request.path_qs}",
            'headers': dict(request.headers),
            'timeout': ClientTimeout(total=route.timeout)
        }
        
        # Add request body if present
        if request.can_read_body:
            request_data['data'] = await request.read()
        
        # Transform request if configured
        if route.transform_request:
            request_data = route.transform_request(request_data)
        
        # Make request
        async with ClientSession() as session:
            async with session.request(**request_data) as response:
                response_data = await response.read()
                
                # Transform response if configured
                if route.transform_response:
                    response_data = route.transform_response(response_data)
                
                return web.Response(
                    body=response_data,
                    status=response.status,
                    headers=response.headers
                )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get gateway metrics."""
        return {
            'metrics': self.metrics.copy(),
            'routes': len(self.routes),
            'rate_limiters': len(self.rate_limiters),
            'load_balancers': len(self.load_balancers)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'routes': len(self.routes),
            'uptime': time.time()
        }

async def create_app() -> web.Application:
    """Create the web application."""
    gateway = APIGateway()
    app = web.Application()
    
    # Add routes
    app.router.add_route('*', '/{path:.*}', gateway.handle_request)
    app.router.add_get('/gateway/metrics', lambda r: web.json_response(gateway.get_metrics()))
    app.router.add_get('/gateway/health', lambda r: web.json_response(gateway.health_check()))
    
    return app

async def main():
    """Main function to run the API Gateway."""
    logging.basicConfig(level=logging.INFO)
    
    app = await create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    print("API Gateway running on http://0.0.0.0:8080")
    print("Health check: http://0.0.0.0:8080/gateway/health")
    print("Metrics: http://0.0.0.0:8080/gateway/metrics")
    
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("Shutting down API Gateway...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())









