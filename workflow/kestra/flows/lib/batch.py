"""
Utilidades para operaciones batch en APIs.

Características:
- Procesamiento paralelo con ThreadPoolExecutor
- Rate limiting por batch
- Retry automático
- Progress tracking
- Resultados agregados
"""
import time
import logging
from typing import List, Dict, Any, Callable, Optional, TypeVar, Generic
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')


@dataclass
class BatchResult(Generic[T, R]):
    """Resultado de una operación batch."""
    total: int
    successful: int
    failed: int
    skipped: int
    success_rate: float
    duration_ms: float
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            "total": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "skipped": self.skipped,
            "success_rate": round(self.success_rate, 2),
            "duration_ms": round(self.duration_ms, 2),
            "results": self.results,
            "errors": self.errors
        }


class BatchProcessor:
    """Procesador de operaciones batch."""
    
    def __init__(
        self,
        max_workers: int = 5,
        batch_delay: float = 0.1,
        retry_on_failure: bool = True,
        max_retries: int = 2
    ):
        """
        Inicializa el procesador batch.
        
        Args:
            max_workers: Número máximo de workers paralelos
            batch_delay: Delay entre batches (segundos)
            retry_on_failure: Si reintentar en caso de fallo
            max_retries: Número máximo de reintentos
        """
        self.max_workers = max_workers
        self.batch_delay = batch_delay
        self.retry_on_failure = retry_on_failure
        self.max_retries = max_retries
        
        logger.info("BatchProcessor initialized", extra={
            "max_workers": max_workers,
            "batch_delay": batch_delay,
            "retry_on_failure": retry_on_failure
        })
    
    def process(
        self,
        items: List[T],
        process_func: Callable[[T], R],
        item_to_dict: Optional[Callable[[T], Dict[str, Any]]] = None,
        result_to_dict: Optional[Callable[[R], Dict[str, Any]]] = None
    ) -> BatchResult[T, R]:
        """
        Procesa una lista de items en paralelo.
        
        Args:
            items: Lista de items a procesar
            process_func: Función que procesa un item
            item_to_dict: Función para convertir item a dict (para logging)
            result_to_dict: Función para convertir resultado a dict
        
        Returns:
            BatchResult con estadísticas y resultados
        """
        start_time = time.time()
        results = []
        errors = []
        successful = 0
        failed = 0
        skipped = 0
        
        def process_item(item: T, attempt: int = 0) -> tuple[bool, Any, Optional[str]]:
            """Procesa un item individual con retry."""
            try:
                result = process_func(item)
                return True, result, None
            except Exception as e:
                if attempt < self.max_retries and self.retry_on_failure:
                    logger.warning(f"Retrying item (attempt {attempt + 1}/{self.max_retries})", extra={
                        "item": str(item)[:100],
                        "error": str(e)
                    })
                    time.sleep(self.batch_delay * (attempt + 1))
                    return process_item(item, attempt + 1)
                else:
                    return False, None, str(e)
        
        # Procesar en paralelo
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(process_item, item): item
                for item in items
            }
            
            for future in as_completed(futures):
                item = futures[future]
                
                try:
                    success, result, error = future.result()
                    
                    item_dict = item_to_dict(item) if item_to_dict else {"item": str(item)}
                    result_dict = result_to_dict(result) if result_to_dict and result else {}
                    
                    if success:
                        successful += 1
                        results.append({
                            **item_dict,
                            "result": result_dict,
                            "status": "success"
                        })
                    else:
                        failed += 1
                        errors.append({
                            **item_dict,
                            "error": error,
                            "status": "failed"
                        })
                        results.append({
                            **item_dict,
                            "status": "failed",
                            "error": error
                        })
                
                except Exception as e:
                    failed += 1
                    item_dict = item_to_dict(item) if item_to_dict else {"item": str(item)}
                    error_msg = str(e)
                    
                    errors.append({
                        **item_dict,
                        "error": error_msg,
                        "status": "failed"
                    })
                    results.append({
                        **item_dict,
                        "status": "failed",
                        "error": error_msg
                    })
                
                # Delay entre items para respetar rate limits
                if self.batch_delay > 0:
                    time.sleep(self.batch_delay)
        
        duration = (time.time() - start_time) * 1000
        total = len(items)
        success_rate = (successful / total * 100) if total > 0 else 0.0
        
        logger.info("Batch processing completed", extra={
            "total": total,
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "success_rate": round(success_rate, 2),
            "duration_ms": round(duration, 2)
        })
        
        return BatchResult(
            total=total,
            successful=successful,
            failed=failed,
            skipped=skipped,
            success_rate=success_rate,
            duration_ms=duration,
            results=results,
            errors=errors
        )
    
    def process_chunks(
        self,
        items: List[T],
        process_func: Callable[[T], R],
        chunk_size: int = 10,
        item_to_dict: Optional[Callable[[T], Dict[str, Any]]] = None,
        result_to_dict: Optional[Callable[[R], Dict[str, Any]]] = None
    ) -> BatchResult[T, R]:
        """
        Procesa items en chunks para mejor control de rate limiting.
        
        Args:
            items: Lista de items a procesar
            process_func: Función que procesa un item
            chunk_size: Tamaño de cada chunk
            item_to_dict: Función para convertir item a dict
            result_to_dict: Función para convertir resultado a dict
        
        Returns:
            BatchResult agregado de todos los chunks
        """
        all_results = []
        all_errors = []
        total_successful = 0
        total_failed = 0
        
        # Procesar en chunks
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            logger.info(f"Processing chunk {i // chunk_size + 1} ({len(chunk)} items)")
            
            chunk_result = self.process(chunk, process_func, item_to_dict, result_to_dict)
            
            all_results.extend(chunk_result.results)
            all_errors.extend(chunk_result.errors)
            total_successful += chunk_result.successful
            total_failed += chunk_result.failed
            
            # Delay entre chunks
            if i + chunk_size < len(items) and self.batch_delay > 0:
                time.sleep(self.batch_delay * 2)  # Delay más largo entre chunks
        
        total = len(items)
        success_rate = (total_successful / total * 100) if total > 0 else 0.0
        
        return BatchResult(
            total=total,
            successful=total_successful,
            failed=total_failed,
            skipped=0,
            success_rate=success_rate,
            duration_ms=sum(r.get("duration_ms", 0) for r in all_results),
            results=all_results,
            errors=all_errors
        )



