#!/usr/bin/env python3
"""
ClickUp Brain Caching System
===========================

High-performance caching system with Redis backend, TTL management,
cache invalidation, and distributed caching support.
"""

import json
import time
import hashlib
import pickle
import asyncio
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
from collections import OrderedDict
import threading
from contextlib import asynccontextmanager

ROOT = Path(__file__).parent

@dataclass
class CacheConfig:
    """Cache configuration settings."""
    backend: str = "redis"  # redis, memory, file
    redis_url: str = "redis://localhost:6379/0"
    default_ttl: int = 3600  # seconds
    max_memory_size: int = 100 * 1024 * 1024  # 100MB
    max_items: int = 10000
    compression: bool = True
    serialization: str = "json"  # json, pickle
    key_prefix: str = "clickup_brain:"
    cluster_mode: bool = False
    cluster_nodes: List[str] = field(default_factory=list)

@dataclass
class CacheStats:
    """Cache statistics."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    memory_usage: int = 0
    item_count: int = 0
    hit_rate: float = 0.0

class MemoryCache:
    """In-memory cache implementation with LRU eviction."""
    
    def __init__(self, max_size: int = 10000, max_memory: int = 100 * 1024 * 1024):
        self.max_size = max_size
        self.max_memory = max_memory
        self.cache: OrderedDict = OrderedDict()
        self.expiry_times: Dict[str, float] = {}
        self.memory_usage = 0
        self.stats = CacheStats()
        self._lock = threading.RLock()
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate memory size of value."""
        try:
            return len(pickle.dumps(value))
        except:
            return 1024  # Default estimate
    
    def _evict_expired(self) -> None:
        """Remove expired items."""
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self.expiry_times.items()
            if expiry <= current_time
        ]
        
        for key in expired_keys:
            self._remove_item(key)
            self.stats.evictions += 1
    
    def _evict_lru(self) -> None:
        """Evict least recently used items."""
        while (len(self.cache) >= self.max_size or 
               self.memory_usage >= self.max_memory):
            if not self.cache:
                break
            
            # Remove least recently used item
            key, value = self.cache.popitem(last=False)
            self.memory_usage -= self._calculate_size(value)
            self.expiry_times.pop(key, None)
            self.stats.evictions += 1
    
    def _remove_item(self, key: str) -> None:
        """Remove item from cache."""
        if key in self.cache:
            value = self.cache.pop(key)
            self.memory_usage -= self._calculate_size(value)
            self.expiry_times.pop(key, None)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            self._evict_expired()
            
            if key in self.cache:
                # Move to end (most recently used)
                value = self.cache.pop(key)
                self.cache[key] = value
                self.stats.hits += 1
                self._update_hit_rate()
                return value
            else:
                self.stats.misses += 1
                self._update_hit_rate()
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        with self._lock:
            self._evict_expired()
            
            # Remove existing item if present
            self._remove_item(key)
            
            # Check if we need to evict
            self._evict_lru()
            
            # Add new item
            self.cache[key] = value
            self.memory_usage += self._calculate_size(value)
            
            if ttl:
                self.expiry_times[key] = time.time() + ttl
            
            self.stats.sets += 1
            self.stats.item_count = len(self.cache)
            return True
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self._lock:
            if key in self.cache:
                self._remove_item(key)
                self.stats.deletes += 1
                self.stats.item_count = len(self.cache)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from cache."""
        with self._lock:
            self.cache.clear()
            self.expiry_times.clear()
            self.memory_usage = 0
            self.stats.item_count = 0
    
    def _update_hit_rate(self) -> None:
        """Update hit rate statistic."""
        total = self.stats.hits + self.stats.misses
        self.stats.hit_rate = self.stats.hits / total if total > 0 else 0.0
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            self.stats.memory_usage = self.memory_usage
            self.stats.item_count = len(self.cache)
            return self.stats

class RedisCache:
    """Redis cache implementation."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", key_prefix: str = "clickup_brain:"):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.stats = CacheStats()
        self._redis = None
        self._lock = threading.RLock()
    
    async def _get_redis(self):
        """Get Redis connection."""
        if self._redis is None:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(self.redis_url)
            except ImportError:
                raise ImportError("redis package is required for Redis backend")
        return self._redis
    
    def _make_key(self, key: str) -> str:
        """Make full cache key with prefix."""
        return f"{self.key_prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            redis_client = await self._get_redis()
            full_key = self._make_key(key)
            
            value = await redis_client.get(full_key)
            if value is not None:
                self.stats.hits += 1
                self._update_hit_rate()
                return json.loads(value)
            else:
                self.stats.misses += 1
                self._update_hit_rate()
                return None
        except Exception as e:
            logging.error(f"Redis get error: {e}")
            self.stats.misses += 1
            self._update_hit_rate()
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        try:
            redis_client = await self._get_redis()
            full_key = self._make_key(key)
            
            serialized_value = json.dumps(value)
            
            if ttl:
                await redis_client.setex(full_key, ttl, serialized_value)
            else:
                await redis_client.set(full_key, serialized_value)
            
            self.stats.sets += 1
            return True
        except Exception as e:
            logging.error(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        try:
            redis_client = await self._get_redis()
            full_key = self._make_key(key)
            
            result = await redis_client.delete(full_key)
            if result:
                self.stats.deletes += 1
                return True
            return False
        except Exception as e:
            logging.error(f"Redis delete error: {e}")
            return False
    
    async def clear(self) -> None:
        """Clear all items from cache."""
        try:
            redis_client = await self._get_redis()
            pattern = f"{self.key_prefix}*"
            keys = await redis_client.keys(pattern)
            if keys:
                await redis_client.delete(*keys)
        except Exception as e:
            logging.error(f"Redis clear error: {e}")
    
    async def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        try:
            redis_client = await self._get_redis()
            info = await redis_client.info('memory')
            
            self.stats.memory_usage = info.get('used_memory', 0)
            self.stats.item_count = await redis_client.dbsize()
            self._update_hit_rate()
            
            return self.stats
        except Exception as e:
            logging.error(f"Redis stats error: {e}")
            return self.stats
    
    def _update_hit_rate(self) -> None:
        """Update hit rate statistic."""
        total = self.stats.hits + self.stats.misses
        self.stats.hit_rate = self.stats.hits / total if total > 0 else 0.0

class CacheManager:
    """Main cache management system."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache_backend = None
        self.logger = logging.getLogger("cache_manager")
        self._lock = threading.RLock()
        
        self._initialize_backend()
    
    def _initialize_backend(self) -> None:
        """Initialize cache backend."""
        if self.config.backend == "redis":
            self.cache_backend = RedisCache(
                redis_url=self.config.redis_url,
                key_prefix=self.config.key_prefix
            )
        elif self.config.backend == "memory":
            self.cache_backend = MemoryCache(
                max_size=self.config.max_items,
                max_memory=self.config.max_memory_size
            )
        else:
            raise ValueError(f"Unsupported cache backend: {self.config.backend}")
    
    def _serialize_key(self, key: Union[str, Dict, List]) -> str:
        """Serialize cache key."""
        if isinstance(key, str):
            return key
        
        # Create hash for complex keys
        key_str = json.dumps(key, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, key: Union[str, Dict, List]) -> Optional[Any]:
        """Get value from cache."""
        serialized_key = self._serialize_key(key)
        return await self.cache_backend.get(serialized_key)
    
    async def set(self, key: Union[str, Dict, List], value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        serialized_key = self._serialize_key(key)
        ttl = ttl or self.config.default_ttl
        return await self.cache_backend.set(serialized_key, value, ttl)
    
    async def delete(self, key: Union[str, Dict, List]) -> bool:
        """Delete value from cache."""
        serialized_key = self._serialize_key(key)
        return await self.cache_backend.delete(serialized_key)
    
    async def clear(self) -> None:
        """Clear all items from cache."""
        await self.cache_backend.clear()
    
    async def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return await self.cache_backend.get_stats()
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        if self.config.backend == "redis":
            try:
                redis_client = await self.cache_backend._get_redis()
                full_pattern = f"{self.config.key_prefix}{pattern}"
                keys = await redis_client.keys(full_pattern)
                if keys:
                    await redis_client.delete(*keys)
                    return len(keys)
            except Exception as e:
                self.logger.error(f"Pattern invalidation error: {e}")
        return 0

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_data = {"args": args, "kwargs": sorted(kwargs.items())}
    return json.dumps(key_data, sort_keys=True)

def cached(ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

@asynccontextmanager
async def cache_lock(key: str, timeout: int = 30):
    """Context manager for cache-based locking."""
    lock_key = f"lock:{key}"
    lock_value = str(time.time())
    
    # Try to acquire lock
    acquired = await cache_manager.set(lock_key, lock_value, timeout)
    
    if acquired:
        try:
            yield
        finally:
            # Release lock
            await cache_manager.delete(lock_key)
    else:
        raise TimeoutError(f"Could not acquire lock for key: {key}")

# Global cache manager instance
cache_manager: Optional[CacheManager] = None

def initialize_cache(config: Optional[CacheConfig] = None) -> CacheManager:
    """Initialize global cache manager."""
    global cache_manager
    if config is None:
        config = CacheConfig()
    
    cache_manager = CacheManager(config)
    return cache_manager

async def get_cache() -> CacheManager:
    """Get global cache manager."""
    global cache_manager
    if cache_manager is None:
        cache_manager = initialize_cache()
    return cache_manager

if __name__ == "__main__":
    # Demo caching system
    print("ClickUp Brain Caching System Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        # Initialize cache
        config = CacheConfig(backend="memory", default_ttl=60)
        cache = initialize_cache(config)
        
        # Test basic operations
        await cache.set("user:123", {"name": "John Doe", "email": "john@example.com"})
        user = await cache.get("user:123")
        print(f"Retrieved user: {user}")
        
        # Test with TTL
        await cache.set("temp:data", "temporary data", ttl=5)
        temp_data = await cache.get("temp:data")
        print(f"Temporary data: {temp_data}")
        
        # Wait for expiration
        print("Waiting for TTL expiration...")
        await asyncio.sleep(6)
        expired_data = await cache.get("temp:data")
        print(f"Expired data: {expired_data}")
        
        # Test cached decorator
        @cached(ttl=30)
        async def expensive_operation(n: int) -> int:
            print(f"Computing expensive operation for {n}")
            await asyncio.sleep(1)  # Simulate expensive operation
            return n * n
        
        # First call - will compute
        result1 = await expensive_operation(5)
        print(f"First call result: {result1}")
        
        # Second call - will use cache
        result2 = await expensive_operation(5)
        print(f"Second call result: {result2}")
        
        # Test cache lock
        async with cache_lock("critical_operation"):
            print("Acquired cache lock, performing critical operation")
            await asyncio.sleep(1)
            print("Critical operation completed")
        
        # Get cache stats
        stats = await cache.get_stats()
        print(f"Cache stats: {stats}")
        
        print("\nCaching system demo completed!")
    
    asyncio.run(demo())







