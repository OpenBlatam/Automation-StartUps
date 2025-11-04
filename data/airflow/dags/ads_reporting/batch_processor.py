"""
Procesamiento por lotes optimizado para grandes volúmenes de datos.

Incluye:
- Chunking inteligente
- Procesamiento paralelo
- Progress tracking
- Manejo de memoria
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
    CONCURRENT_AVAILABLE = True
except ImportError:
    CONCURRENT_AVAILABLE = False

try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False


@dataclass
class BatchResult:
    """Resultado de procesamiento en batch."""
    total: int
    processed: int
    successful: int
    failed: int
    duration_ms: float
    results: List[Any]
    errors: List[Dict[str, Any]]
    
    @property
    def success_rate(self) -> float:
        """Tasa de éxito en porcentaje."""
        if self.total == 0:
            return 0.0
        return (self.successful / self.total) * 100.0
    
    @property
    def throughput(self) -> float:
        """Throughput en registros por segundo."""
        if self.duration_ms == 0:
            return 0.0
        return (self.processed / (self.duration_ms / 1000))


class BatchProcessor:
    """Procesador de lotes optimizado."""
    
    def __init__(
        self,
        chunk_size: int = 100,
        max_workers: int = 5,
        use_multiprocessing: bool = False
    ):
        """
        Inicializa el procesador de lotes.
        
        Args:
            chunk_size: Tamaño de cada chunk
            max_workers: Número máximo de workers
            use_multiprocessing: Si usar multiprocessing en lugar de threading
        """
        self.chunk_size = chunk_size
        self.max_workers = max_workers
        self.use_multiprocessing = use_multiprocessing
    
    def process_in_chunks(
        self,
        data: List[Any],
        processor_func: Callable[[List[Any]], Any],
        continue_on_error: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> BatchResult:
        """
        Procesa datos en chunks.
        
        Args:
            data: Lista de datos a procesar
            processor_func: Función que procesa un chunk
            continue_on_error: Si continuar cuando hay errores
            progress_callback: Callback para reportar progreso (processed, total)
            
        Returns:
            BatchResult con resultados
        """
        start_time = time.time()
        total = len(data)
        
        # Dividir en chunks
        chunks = [
            data[i:i + self.chunk_size]
            for i in range(0, total, self.chunk_size)
        ]
        
        results = []
        errors = []
        processed = 0
        successful = 0
        failed = 0
        
        logger.info(f"Procesando {total} items en {len(chunks)} chunks")
        
        # Procesar chunks
        if CONCURRENT_AVAILABLE and self.max_workers > 1 and len(chunks) > 1:
            # Procesamiento paralelo
            executor_class = ProcessPoolExecutor if self.use_multiprocessing else ThreadPoolExecutor
            
            with executor_class(max_workers=self.max_workers) as executor:
                future_to_chunk = {
                    executor.submit(processor_func, chunk): i
                    for i, chunk in enumerate(chunks)
                }
                
                for future in as_completed(future_to_chunk):
                    chunk_idx = future_to_chunk[future]
                    try:
                        result = future.result()
                        results.append(result)
                        successful += 1
                        processed += len(chunks[chunk_idx])
                    except Exception as e:
                        failed += 1
                        errors.append({
                            "chunk": chunk_idx,
                            "error": str(e),
                            "chunk_size": len(chunks[chunk_idx])
                        })
                        logger.error(f"Error procesando chunk {chunk_idx}: {str(e)}")
                        
                        if not continue_on_error:
                            break
                    
                    if progress_callback:
                        progress_callback(processed, total)
        else:
            # Procesamiento secuencial
            for i, chunk in enumerate(chunks):
                try:
                    result = processor_func(chunk)
                    results.append(result)
                    successful += 1
                    processed += len(chunk)
                except Exception as e:
                    failed += 1
                    errors.append({
                        "chunk": i,
                        "error": str(e),
                        "chunk_size": len(chunk)
                    })
                    logger.error(f"Error procesando chunk {i}: {str(e)}")
                    
                    if not continue_on_error:
                        break
                
                if progress_callback:
                    progress_callback(processed, total)
        
        duration_ms = (time.time() - start_time) * 1000
        
        result = BatchResult(
            total=total,
            processed=processed,
            successful=successful,
            failed=failed,
            duration_ms=duration_ms,
            results=results,
            errors=errors
        )
        
        logger.info(
            f"Batch processing completado: {successful}/{len(chunks)} chunks exitosos "
            f"({result.success_rate:.2f}%), throughput: {result.throughput:.2f} items/s"
        )
        
        # Trackear métricas
        if STATS_AVAILABLE:
            try:
                stats = Stats()
                stats.incr("ads_reporting.batch.total", total)
                stats.incr("ads_reporting.batch.successful", successful)
                stats.incr("ads_reporting.batch.failed", failed)
                stats.timing("ads_reporting.batch.duration_ms", int(duration_ms))
                stats.gauge("ads_reporting.batch.throughput", result.throughput)
            except Exception:
                pass
        
        return result
    
    def adaptive_chunk_size(
        self,
        total_items: int,
        target_chunks: int = 10
    ) -> int:
        """
        Calcula tamaño de chunk adaptativo.
        
        Args:
            total_items: Total de items
            target_chunks: Número objetivo de chunks
            
        Returns:
            Tamaño de chunk calculado
        """
        if total_items == 0:
            return self.chunk_size
        
        calculated = max(1, total_items // target_chunks)
        
        # Limitar entre 10 y 1000
        return max(10, min(calculated, 1000))


def process_campaign_batch(
    data: List[Dict[str, Any]],
    processor_func: Callable[[Dict[str, Any]], Any],
    chunk_size: int = 100,
    max_workers: int = 5
) -> BatchResult:
    """
    Procesa una lista de campañas en batch.
    
    Args:
        data: Lista de datos de campañas
        processor_func: Función que procesa un registro
        chunk_size: Tamaño de chunk
        max_workers: Número de workers
        
    Returns:
        BatchResult
    """
    batch_processor = BatchProcessor(chunk_size=chunk_size, max_workers=max_workers)
    
    def process_chunk(chunk: List[Dict[str, Any]]) -> List[Any]:
        """Procesa un chunk de datos."""
        chunk_results = []
        for item in chunk:
            try:
                result = processor_func(item)
                chunk_results.append(result)
            except Exception as e:
                logger.warning(f"Error procesando item: {str(e)}")
                chunk_results.append(None)
        return chunk_results
    
    return batch_processor.process_in_chunks(data, process_chunk)

