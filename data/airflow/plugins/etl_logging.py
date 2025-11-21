from __future__ import annotations

import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager


def get_task_logger(task_name: str | None = None) -> logging.Logger:
	"""
	Get a logger configured with task context.
	
	Args:
		task_name: Optional task identifier for context
		
	Returns:
		Logger instance with structured context support
	"""
	logger = logging.getLogger("airflow.task")
	if task_name:
		logger = logging.getLogger(f"airflow.task.{task_name}")
	return logger


def log_with_context(
	logger: logging.Logger,
	level: int,
	message: str,
	task_id: str | None = None,
	dag_run_id: str | None = None,
	chunk: str | None = None,
	**extra: Any,
) -> None:
	"""
	Log with structured context for better correlation.
	
	Args:
		logger: Logger instance
		level: Log level (logging.INFO, logging.ERROR, etc.)
		message: Log message
		task_id: Task identifier for correlation
		dag_run_id: DAG run identifier for correlation
		chunk: Chunk/index for mapped tasks
		**extra: Additional structured fields
	"""
	context_extra: Dict[str, Any] = {}
	if task_id:
		context_extra["task_id"] = task_id
	if dag_run_id:
		context_extra["dag_run_id"] = dag_run_id
	if chunk is not None:
		context_extra["chunk"] = chunk
	context_extra.update(extra)
	logger.log(level, message, extra=context_extra)


@contextmanager
def log_task_duration(
	logger: logging.Logger,
	task_name: str,
	**context: Any,
):
	"""
	Context manager to log task execution duration.
	
	Example:
		with log_task_duration(logger, "transform", chunk=0):
			# do work
	"""
	import time
	start = time.perf_counter()
	try:
		yield
	finally:
		duration_ms = int((time.perf_counter() - start) * 1000)
		log_with_context(
			logger,
			logging.INFO,
			f"{task_name} completed",
			duration_ms=duration_ms,
			**context,
		)


