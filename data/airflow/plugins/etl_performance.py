from __future__ import annotations

import time
from typing import Dict, Any, Optional
from contextlib import contextmanager


class PerformanceTracker:
	"""Track performance metrics with percentiles and distributions."""
	
	def __init__(self, task_name: str):
		self.task_name = task_name
		self.durations: list[float] = []
	
	def record(self, duration_ms: float) -> None:
		"""Record a duration measurement."""
		self.durations.append(duration_ms)
	
	def get_stats(self) -> Dict[str, float]:
		"""Calculate performance statistics."""
		if not self.durations:
			return {}
		
		sorted_durs = sorted(self.durations)
		n = len(sorted_durs)
		
		return {
			"count": n,
			"min_ms": min(sorted_durs),
			"max_ms": max(sorted_durs),
			"mean_ms": sum(sorted_durs) / n,
			"p50_ms": sorted_durs[n // 2],
			"p95_ms": sorted_durs[int(n * 0.95)] if n > 1 else sorted_durs[0],
			"p99_ms": sorted_durs[int(n * 0.99)] if n > 1 else sorted_durs[0],
		}
	
	def report(self) -> None:
		"""Report statistics to Stats backend."""
		try:
			from airflow.stats import Stats
			stats = self.get_stats()
			if stats:
				Stats.gauge(f"etl_example.perf.{self.task_name}.count", stats["count"])
				Stats.timing(f"etl_example.perf.{self.task_name}.min_ms", stats["min_ms"])
				Stats.timing(f"etl_example.perf.{self.task_name}.max_ms", stats["max_ms"])
				Stats.timing(f"etl_example.perf.{self.task_name}.mean_ms", stats["mean_ms"])
				Stats.timing(f"etl_example.perf.{self.task_name}.p50_ms", stats["p50_ms"])
				Stats.timing(f"etl_example.perf.{self.task_name}.p95_ms", stats["p95_ms"])
				Stats.timing(f"etl_example.perf.{self.task_name}.p99_ms", stats["p99_ms"])
		except Exception:
			pass


@contextmanager
def track_performance(task_name: str, report: bool = True):
	"""
	Context manager to track and report performance metrics.
	
	Example:
		with track_performance("transform"):
			# do work
	"""
	start = time.perf_counter()
	try:
		yield
	finally:
		duration_ms = (time.perf_counter() - start) * 1000
		if report:
			tracker = PerformanceTracker(task_name)
			tracker.record(duration_ms)
			tracker.report()


