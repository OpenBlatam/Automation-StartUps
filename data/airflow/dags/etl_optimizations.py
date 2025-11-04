"""
Optimizaciones adicionales para etl_example.py

Estas funciones pueden integrarse para mejorar rendimiento y observabilidad.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def optimized_make_chunks_logic(
	rows: int,
	base_chunk_rows: int,
	max_chunks: int,
	adaptive_func: callable
) -> tuple[list[Dict[str, Any]], int]:
	"""Lógica optimizada para crear chunks con sizing adaptativo.
	
	Returns:
		Tuple of (chunks_list, optimal_chunk_size)
	"""
	if rows <= 0:
		return [], 0
	
	if base_chunk_rows <= 0:
		base_chunk_rows = rows
		logger.warning("Invalid chunk_rows, using full rows", extra={"chunk_rows": base_chunk_rows, "rows": rows})
	
	optimal_chunk_rows = adaptive_func(rows, max_chunks, base_chunk_rows)
	
	if optimal_chunk_rows != base_chunk_rows:
		logger.info("Adaptive sizing applied", extra={
			"base_chunk_rows": base_chunk_rows,
			"optimal_chunk_rows": optimal_chunk_rows,
			"rows": rows,
			"max_chunks": max_chunks
		})
	
	chunks: list[Dict[str, Any]] = []
	remaining = rows
	while remaining > 0:
		part = min(optimal_chunk_rows, remaining)
		chunks.append({"rows": part, "transformed": False})
		remaining -= part
	
	return chunks, optimal_chunk_rows


def enhanced_volume_anomaly_check(
	current_rows: int,
	history: list[int],
	threshold_factor: float = 2.0,
	min_samples: int = 3
) -> tuple[bool, float, float]:
	"""Mejora la detección de anomalías con más estadísticas.
	
	Returns:
		Tuple of (is_anomaly, avg_rows, std_dev)
	"""
	if len(history) < min_samples:
		return False, 0.0, 0.0
	
	import statistics
	
	avg = statistics.mean(history)
	std = statistics.stdev(history) if len(history) > 1 else 0.0
	
	# Anomaly if outside 2 standard deviations or threshold_factor multiplier
	is_anomaly = (
		current_rows > threshold_factor * max(history) or
		current_rows < (1.0 / threshold_factor) * min(history) or
		(abs(current_rows - avg) > 2 * std and std > 0)
	)
	
	return is_anomaly, avg, std


