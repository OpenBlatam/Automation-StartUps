from __future__ import annotations

import time
import logging
from typing import Callable, Any, TypeVar
from functools import wraps
from airflow.models import Variable

T = TypeVar("T")

_logger = logging.getLogger(__name__)


def _rate_limit_key(task_name: str) -> str:
	"""Variable key for rate limit state."""
	return f"rate_limit:{task_name}"


def rate_limit(
	max_calls: int = 10,
	window_seconds: int = 60,
	variable_key: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
	"""
	Decorator to enforce rate limiting on task execution.
	
	Uses Airflow Variables to track call counts within a time window.
	
	Args:
		max_calls: Maximum number of calls allowed within window_seconds
		window_seconds: Time window in seconds for rate limiting
		variable_key: Optional custom key for state storage (defaults to task name)
		
	Example:
		@rate_limit(max_calls=5, window_seconds=60)
		def my_api_call():
			...
	"""
	def decorator(func: Callable[..., T]) -> Callable[..., T]:
		task_name = variable_key or func.__name__
		
		@wraps(func)
		def wrapper(*args: Any, **kwargs: Any) -> T:
			key = _rate_limit_key(task_name)
			now_ts = int(time.time())
			
			try:
				data_str = Variable.get(key, default_var=None)
				if data_str:
					import json
					data = json.loads(data_str)
					window_start = int(data.get("window_start", 0))
					count = int(data.get("count", 0))
					
					# Reset if window expired
					if now_ts - window_start >= window_seconds:
						count = 0
						window_start = now_ts
				else:
					count = 0
					window_start = now_ts
				
				# Check limit
				if count >= max_calls:
					wait_seconds = window_seconds - (now_ts - window_start)
					if wait_seconds > 0:
						_logger.warning(
							"Rate limit exceeded, waiting %ds",
							wait_seconds,
							extra={
								"task": task_name,
								"calls": count,
								"max": max_calls,
								"window_sec": window_seconds,
							}
						)
						# Record rate limit hit metric
						try:
							from airflow.stats import Stats
							Stats.incr(f"rate_limit.{task_name}.hits", 1)
						except Exception:
							pass
						time.sleep(min(wait_seconds, 60))  # cap wait at 60s
						# Reset after wait
						count = 0
						window_start = int(time.time())
				
				# Increment and store
				count += 1
				Variable.set(key, json.dumps({
					"window_start": window_start,
					"count": count,
				}))
				
			except Exception as e:
				_logger.warning("Rate limit check failed, proceeding: %s", e)
			
			return func(*args, **kwargs)
		
		return wrapper
	return decorator

