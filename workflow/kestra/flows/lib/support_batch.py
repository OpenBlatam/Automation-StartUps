"""
Sistema de Procesamiento por Lotes para Tickets de Soporte.

Características:
- Procesamiento batch de múltiples tickets
- Optimización de llamadas a APIs
- Rate limiting inteligente
- Retry con exponential backoff
- Métricas de batch processing
"""
import logging
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """Resultado de procesamiento batch."""
    total: int
    successful: int
    failed: int
    duration_seconds: float
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]


class SupportBatchProcessor:
    """Procesador batch para tickets de soporte."""
    
    def __init__(
        self,
        batch_size: int = 10,
        max_workers: int = 5,
        rate_limit_per_second: int = 10,
        enable_retry: bool = True,
        max_retries: int = 3
    ):
        """
        Inicializa el procesador batch.
        
        Args:
            batch_size: Tamaño de cada batch
            max_workers: Número máximo de workers paralelos
            rate_limit_per_second: Límite de requests por segundo
            enable_retry: Habilitar retry automático
            max_retries: Número máximo de reintentos
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.rate_limit_per_second = rate_limit_per_second
        self.enable_retry = enable_retry
        self.max_retries = max_retries
        self.last_request_time = 0.0
        self.min_request_interval = 1.0 / rate_limit_per_second
    
    def _rate_limit(self):
        """Aplica rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _process_item_with_retry(
        self,
        item: Dict[str, Any],
        process_func: Callable
    ) -> Dict[str, Any]:
        """Procesa un item con retry."""
        if not self.enable_retry or not TENACITY_AVAILABLE:
            return process_func(item)
        
        @retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(Exception)
        )
        def _retry_process():
            self._rate_limit()
            return process_func(item)
        
        try:
            return _retry_process()
        except Exception as e:
            logger.error(f"Failed to process item after retries: {e}")
            return {
                "item": item,
                "success": False,
                "error": str(e)
            }
    
    def process_batch(
        self,
        items: List[Dict[str, Any]],
        process_func: Callable,
        parallel: bool = False
    ) -> BatchResult:
        """
        Procesa un batch de items.
        
        Args:
            items: Lista de items a procesar
            process_func: Función para procesar cada item
            parallel: Si usar procesamiento paralelo
            
        Returns:
            BatchResult con resultados
        """
        start_time = datetime.now()
        results = []
        errors = []
        successful = 0
        failed = 0
        
        if parallel and self.max_workers > 1:
            try:
                from concurrent.futures import ThreadPoolExecutor, as_completed
                
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = {
                        executor.submit(
                            self._process_item_with_retry,
                            item,
                            process_func
                        ): item for item in items
                    }
                    
                    for future in as_completed(futures):
                        result = future.result()
                        if result.get("success", False):
                            results.append(result)
                            successful += 1
                        else:
                            errors.append(result)
                            failed += 1
            except ImportError:
                logger.warning("concurrent.futures not available, using sequential")
                parallel = False
        
        if not parallel:
            # Procesamiento secuencial
            for item in items:
                try:
                    result = self._process_item_with_retry(item, process_func)
                    if result.get("success", False):
                        results.append(result)
                        successful += 1
                    else:
                        errors.append(result)
                        failed += 1
                except Exception as e:
                    logger.error(f"Error processing item: {e}")
                    errors.append({
                        "item": item,
                        "success": False,
                        "error": str(e)
                    })
                    failed += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return BatchResult(
            total=len(items),
            successful=successful,
            failed=failed,
            duration_seconds=duration,
            results=results,
            errors=errors
        )
    
    def process_in_batches(
        self,
        items: List[Dict[str, Any]],
        process_func: Callable,
        parallel: bool = False
    ) -> List[BatchResult]:
        """
        Procesa items en batches.
        
        Args:
            items: Lista de items a procesar
            process_func: Función para procesar cada item
            parallel: Si usar procesamiento paralelo
            
        Returns:
            Lista de BatchResult por cada batch
        """
        batch_results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            logger.info(f"Processing batch {i // self.batch_size + 1} ({len(batch)} items)")
            
            result = self.process_batch(batch, process_func, parallel)
            batch_results.append(result)
            
            logger.info(
                f"Batch {i // self.batch_size + 1} completed: "
                f"{result.successful}/{result.total} successful, "
                f"duration: {result.duration_seconds:.2f}s"
            )
        
        return batch_results


def batch_prioritize_tickets(
    tickets: List[Dict[str, Any]],
    calculator: Any,
    batch_size: int = 20
) -> List[Dict[str, Any]]:
    """
    Prioriza múltiples tickets en batch.
    
    Args:
        tickets: Lista de tickets a priorizar
        calculator: Instancia de SupportPriorityCalculator
        batch_size: Tamaño del batch
        
    Returns:
        Lista de tickets con prioridad calculada
    """
    processor = SupportBatchProcessor(batch_size=batch_size)
    
    def process_ticket(ticket: Dict[str, Any]) -> Dict[str, Any]:
        priority = calculator.calculate_priority(
            subject=ticket.get("subject", ""),
            description=ticket.get("description", ""),
            customer_email=ticket.get("customer_email", ""),
            customer_id=ticket.get("customer_id"),
            source=ticket.get("source", "web"),
            category=ticket.get("category")
        )
        
        return {
            "success": True,
            "ticket_id": ticket.get("ticket_id"),
            "priority": priority.priority,
            "priority_score": priority.score,
            "factors": priority.factors
        }
    
    results = processor.process_in_batches(tickets, process_ticket)
    
    # Consolidar resultados
    prioritized_tickets = []
    for batch_result in results:
        for result in batch_result.results:
            if result.get("success"):
                prioritized_tickets.append(result)
    
    return prioritized_tickets

