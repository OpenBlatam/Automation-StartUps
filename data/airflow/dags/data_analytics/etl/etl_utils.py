"""
Utility functions for ETL operations.
"""
import logging
import time
from typing import Dict, Any, Optional
from datetime import timedelta

logger = logging.getLogger(__name__)


def calculate_throughput(rows: int, duration_seconds: float) -> Optional[float]:
	"""
	Calculate throughput in rows per second.
	
	Args:
		rows: Number of rows processed
		duration_seconds: Duration in seconds
		
	Returns:
		Throughput in rows/second, or None if calculation invalid
	"""
	if duration_seconds <= 0 or rows <= 0:
		return None
	return rows / duration_seconds


def format_duration(milliseconds: int) -> str:
	"""
	Format duration in human-readable format.
	
	Args:
		milliseconds: Duration in milliseconds
		
	Returns:
		Formatted string (e.g., "2.5s", "1m 30s", "1h 5m")
	"""
	if milliseconds < 1000:
		return f"{milliseconds}ms"
	
	seconds = milliseconds / 1000.0
	
	if seconds < 60:
		return f"{seconds:.1f}s"
	
	minutes = int(seconds // 60)
	remaining_seconds = seconds % 60
	
	if minutes < 60:
		return f"{minutes}m {remaining_seconds:.1f}s"
	
	hours = minutes // 60
	remaining_minutes = minutes % 60
	return f"{hours}h {remaining_minutes}m {remaining_seconds:.1f}s"


def format_window_info(since: Optional[str], until: Optional[str]) -> str:
	"""
	Format window information for display.
	
	Args:
		since: Start timestamp (ISO format)
		until: End timestamp (ISO format)
		
	Returns:
		Formatted window string
	"""
	if not since and not until:
		return ""
	
	since_part = since[:10] if since else "start"
	until_part = until[:10] if until else "now"
	return f"{since_part}..{until_part}"


def validate_time_window(since: Optional[str], until: Optional[str], max_days: int = 30) -> tuple[bool, Optional[str]]:
	"""
	Validate time window parameters.
	
	Args:
		since: Start timestamp
		until: End timestamp
		max_days: Maximum allowed window size in days
		
	Returns:
		Tuple of (is_valid, error_message)
	"""
	try:
		import pendulum
		
		if not since:
			return True, None
		
		ts_since = pendulum.parse(since)
		ts_until = pendulum.parse(until) if until else pendulum.now("UTC")
		
		if ts_until < ts_since:
			return False, "until must be >= since"
		
		delta_days = (ts_until - ts_since).days
		if delta_days > max_days:
			return False, f"window too large: {delta_days}d > {max_days}d"
		
		return True, None
	except Exception as e:
		return False, f"Invalid timestamp format: {e}"


def retry_with_jitter(max_jitter_seconds: float = 3.0) -> None:
	"""
	Sleep for a random duration to add jitter on retries.
	
	Args:
		max_jitter_seconds: Maximum jitter duration in seconds
	"""
	import random
	jitter = random.uniform(0, max_jitter_seconds)
	time.sleep(jitter)


def log_task_metrics(
	task_name: str,
	rows: int,
	duration_ms: int,
	success: bool = True,
	extra_context: Optional[Dict[str, Any]] = None
) -> None:
	"""
	Log comprehensive task metrics.
	
	Args:
		task_name: Name of the task
		rows: Number of rows processed
		duration_ms: Duration in milliseconds
		success: Whether the task succeeded
		extra_context: Additional context to log
	"""
	extra = {
		"task": task_name,
		"rows": rows,
		"duration_ms": duration_ms,
		"duration_formatted": format_duration(duration_ms),
		"success": success,
	}
	
	if duration_ms > 0 and rows > 0:
		throughput = calculate_throughput(rows, duration_ms / 1000.0)
		if throughput:
			extra["throughput_rows_per_sec"] = throughput
	
	if extra_context:
		extra.update(extra_context)
	
	level = logging.INFO if success else logging.WARNING
	logger.log(level, "task_metrics", extra=extra)


