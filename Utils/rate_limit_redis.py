import os
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import redis
except Exception:
    redis = None

class RedisRateLimiter:
    def __init__(self, redis_url: Optional[str] = None, window_seconds: int = 60):
        self.redis_url = redis_url or os.getenv('REDIS_URL')
        self.window_seconds = window_seconds
        self.enabled = bool(self.redis_url and redis is not None)
        self._client = None
        if self.enabled:
            try:
                self._client = redis.from_url(self.redis_url, decode_responses=True)
            except Exception as e:
                logger.warning(f'No se pudo conectar a Redis: {e}')
                self.enabled = False

    def is_allowed(self, key: str, limit: int) -> tuple[bool, int]:
        if not self.enabled:
            return True, limit
        now = int(time.time())
        bucket_key = f"rl:{key}:{now // self.window_seconds}"
        try:
            pipe = self._client.pipeline()
            pipe.incr(bucket_key, 1)
            pipe.expire(bucket_key, self.window_seconds)
            current = pipe.execute()[0]
            remaining = max(0, limit - int(current))
            return (current <= limit), remaining
        except Exception as e:
            logger.warning(f'Fallo rate limit Redis: {e}')
            return True, limit

rate_limiter = RedisRateLimiter()

