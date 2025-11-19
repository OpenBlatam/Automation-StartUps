"""
Decoradores útiles para ads reporting.

Incluye:
- Retry decorators
- Cache decorators
- Validation decorators
- Metrics decorators
- Error handling decorators
"""

from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable, Dict, Optional, TypeVar, ParamSpec

logger = logging.getLogger(__name__)

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

try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

P = ParamSpec('P')
R = TypeVar('R')


def with_retry(
    max_attempts: int = 3,
    backoff: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorador para agregar retry logic a funciones.
    
    Args:
        max_attempts: Número máximo de intentos
        backoff: Factor de backoff exponencial
        exceptions: Tupla de excepciones a retry
        
    Ejemplo:
        @with_retry(max_attempts=5, backoff=2.0)
        def my_function():
            ...
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        if TENACITY_AVAILABLE:
            @retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(multiplier=backoff, min=1, max=10),
                retry=retry_if_exception_type(exceptions),
                reraise=True
            )
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return func(*args, **kwargs)
        else:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                last_exception = None
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            wait_time = backoff * (2 ** attempt)
                            logger.warning(
                                f"Intento {attempt + 1}/{max_attempts} falló: {str(e)}. "
                                f"Reintentando en {wait_time}s"
                            )
                            time.sleep(min(wait_time, 10))
                        else:
                            raise
                
                if last_exception:
                    raise last_exception
                raise RuntimeError("Función falló sin excepción")
        
        return wrapper
    return decorator


def with_cache(
    cache_key_func: Optional[Callable] = None,
    ttl: int = 300
):
    """
    Decorador para agregar caché a funciones.
    
    Args:
        cache_key_func: Función para generar clave de caché (opcional)
        ttl: Tiempo de vida en segundos
        
    Ejemplo:
        @with_cache(ttl=600)
        def expensive_operation(param1, param2):
            ...
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        try:
            from ads_reporting.cache import get_cache
            cache = get_cache(ttl=ttl)
        except ImportError:
            cache = None
            logger.warning("Cache no disponible")
        
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if cache is None:
                return func(*args, **kwargs)
            
            # Generar clave de caché
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                # Generar clave automática
                key_parts = [str(args), str(sorted(kwargs.items()))]
                cache_key = hash(tuple(key_parts))
            
            # Intentar obtener del caché
            cached_result = cache.get("decorator", func.__name__, {"key": str(cache_key)})
            if cached_result is not None:
                logger.debug(f"Resultado obtenido del caché para {func.__name__}")
                return cached_result
            
            # Ejecutar función y guardar en caché
            result = func(*args, **kwargs)
            cache.set("decorator", func.__name__, {"key": str(cache_key)}, result)
            
            return result
        
        return wrapper
    return decorator


def with_validation(
    validator_func: Optional[Callable] = None,
    validate_input: bool = False,
    validate_output: bool = True
):
    """
    Decorador para agregar validación a funciones.
    
    Args:
        validator_func: Función de validación (opcional)
        validate_input: Si validar inputs
        validate_output: Si validar outputs
        
    Ejemplo:
        @with_validation(validate_output=True)
        def extract_data(...):
            ...
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Validar inputs si está habilitado
            if validate_input and validator_func:
                validator_func(*args, **kwargs)
            
            # Ejecutar función
            result = func(*args, **kwargs)
            
            # Validar outputs si está habilitado
            if validate_output and validator_func:
                validator_func(result)
            
            return result
        
        return wrapper
    return decorator


def track_metrics(
    metric_name: str,
    tags: Optional[Dict[str, str]] = None
):
    """
    Decorador para trackear métricas de funciones.
    
    Args:
        metric_name: Nombre de la métrica
        tags: Tags adicionales para la métrica
        
    Ejemplo:
        @track_metrics("extract_campaigns", tags={"platform": "facebook"})
        def extract(...):
            ...
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start_time = time.time()
            full_tags = {**(tags or {}), "function": func.__name__}
            
            if STATS_AVAILABLE:
                try:
                    stats = Stats()
                    stats.incr(f"{metric_name}.start", tags=full_tags)
                except Exception:
                    pass
            
            try:
                result = func(*args, **kwargs)
                
                if STATS_AVAILABLE:
                    try:
                        stats = Stats()
                        duration_ms = (time.time() - start_time) * 1000
                        stats.incr(f"{metric_name}.success", tags=full_tags)
                        stats.timing(f"{metric_name}.duration_ms", int(duration_ms), tags=full_tags)
                    except Exception:
                        pass
                
                return result
                
            except Exception as e:
                if STATS_AVAILABLE:
                    try:
                        stats = Stats()
                        stats.incr(
                            f"{metric_name}.error",
                            tags={**full_tags, "error_type": type(e).__name__}
                        )
                    except Exception:
                        pass
                raise
        
        return wrapper
    return decorator


def handle_errors(
    error_handler: Optional[Callable[[Exception], Any]] = None,
    default_return: Any = None,
    log_errors: bool = True
):
    """
    Decorador para manejar errores de forma centralizada.
    
    Args:
        error_handler: Función para manejar errores (opcional)
        default_return: Valor a retornar en caso de error (opcional)
        log_errors: Si loguear errores
        
    Ejemplo:
        @handle_errors(default_return=[])
        def risky_function():
            ...
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(
                        f"Error en {func.__name__}: {str(e)}",
                        exc_info=True,
                        extra={
                            "function": func.__name__,
                            "args": str(args)[:100],  # Limitar tamaño
                            "kwargs_keys": list(kwargs.keys())
                        }
                    )
                
                if error_handler:
                    return error_handler(e)
                
                if default_return is not None:
                    return default_return
                
                raise
        
        return wrapper
    return decorator


def timeout(seconds: int = 30):
    """
    Decorador para agregar timeout a funciones.
    
    Args:
        seconds: Timeout en segundos
        
    Ejemplo:
        @timeout(seconds=60)
        def slow_function():
            ...
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Función {func.__name__} excedió timeout de {seconds}s")
            
            # Configurar timeout (solo funciona en main thread)
            try:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(seconds)
                
                try:
                    result = func(*args, **kwargs)
                finally:
                    signal.alarm(0)  # Cancelar alarm
                
                return result
            except (ValueError, AttributeError):
                # Signal no disponible (Windows o sub-thread)
                logger.warning(f"Timeout no disponible para {func.__name__}")
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def log_execution(
    log_args: bool = False,
    log_result: bool = False
):
    """
    Decorador para loguear ejecución de funciones.
    
    Args:
        log_args: Si loguear argumentos
        log_result: Si loguear resultado
        
    Ejemplo:
        @log_execution(log_args=True, log_result=False)
        def important_function(param1, param2):
            ...
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start_time = time.time()
            
            if log_args:
                logger.info(
                    f"Ejecutando {func.__name__}",
                    extra={
                        "args_count": len(args),
                        "kwargs": list(kwargs.keys()) if not log_result else kwargs
                    }
                )
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"{func.__name__} completado en {duration:.2f}s",
                    extra={"duration_seconds": duration}
                )
                
                if log_result:
                    logger.debug(f"Resultado de {func.__name__}: {result}")
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"{func.__name__} falló después de {duration:.2f}s: {str(e)}",
                    extra={"duration_seconds": duration}
                )
                raise
        
        return wrapper
    return decorator


def combine_decorators(*decorators):
    """
    Combina múltiples decoradores en uno.
    
    Ejemplo:
        @combine_decorators(
            with_retry(max_attempts=3),
            track_metrics("my_operation"),
            log_execution()
        )
        def my_function():
            ...
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        for dec in decorators:
            func = dec(func)
        return func
    return decorator

