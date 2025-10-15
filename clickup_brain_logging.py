#!/usr/bin/env python3
"""
ClickUp Brain Logging Framework
==============================

Structured logging with file rotation, levels, and performance monitoring.
"""

import logging
import logging.handlers
import sys
import time
import json
import traceback
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime
from contextlib import contextmanager
import threading
from dataclasses import dataclass, asdict

ROOT = Path(__file__).parent

@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: str
    level: str
    logger: str
    message: str
    module: str = ""
    function: str = ""
    line: int = 0
    thread_id: str = ""
    process_id: int = 0
    extra_data: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        if self.extra_data:
            data['extra_data'] = self.extra_data
        return data

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def __init__(self, use_json: bool = False):
        super().__init__()
        self.use_json = use_json
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured data."""
        log_entry = LogEntry(
            timestamp=datetime.fromtimestamp(record.created).isoformat(),
            level=record.levelname,
            logger=record.name,
            message=record.getMessage(),
            module=record.module or "",
            function=record.funcName or "",
            line=record.lineno or 0,
            thread_id=str(record.thread),
            process_id=record.process,
            extra_data=getattr(record, 'extra_data', None)
        )
        
        if self.use_json:
            return json.dumps(log_entry.to_dict(), default=str)
        else:
            return f"{log_entry.timestamp} [{log_entry.level}] {log_entry.logger}:{log_entry.function}:{log_entry.line} - {log_entry.message}"

class PerformanceLogger:
    """Performance monitoring and logging."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._timers: Dict[str, float] = {}
        self._counters: Dict[str, int] = {}
        self._lock = threading.Lock()
    
    @contextmanager
    def timer(self, operation: str, extra_data: Optional[Dict[str, Any]] = None):
        """Context manager for timing operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            with self._lock:
                self._timers[operation] = duration
            
            self.logger.info(
                f"Operation '{operation}' completed",
                extra={
                    'extra_data': {
                        'operation': operation,
                        'duration_seconds': duration,
                        **(extra_data or {})
                    }
                }
            )
    
    def increment_counter(self, counter_name: str, value: int = 1) -> None:
        """Increment a performance counter."""
        with self._lock:
            self._counters[counter_name] = self._counters.get(counter_name, 0) + value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        with self._lock:
            return {
                'timers': self._timers.copy(),
                'counters': self._counters.copy()
            }
    
    def reset_stats(self) -> None:
        """Reset performance statistics."""
        with self._lock:
            self._timers.clear()
            self._counters.clear()

class ClickUpBrainLogger:
    """Main logging system for ClickUp Brain."""
    
    def __init__(self, 
                 name: str = "clickup_brain",
                 level: str = "INFO",
                 log_file: Optional[Path] = None,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 console_output: bool = True,
                 use_json: bool = False):
        
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        self.formatter = StructuredFormatter(use_json=use_json)
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(self.formatter)
            self.logger.addHandler(console_handler)
        
        # File handler with rotation
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
        
        # Performance logger
        self.performance = PerformanceLogger(self.logger)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def debug(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, extra_data)
    
    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        self._log(logging.INFO, message, extra_data)
    
    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, extra_data)
    
    def error(self, message: str, extra_data: Optional[Dict[str, Any]] = None, exc_info: bool = True) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, extra_data, exc_info)
    
    def critical(self, message: str, extra_data: Optional[Dict[str, Any]] = None, exc_info: bool = True) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, message, extra_data, exc_info)
    
    def _log(self, level: int, message: str, extra_data: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Internal logging method."""
        extra = {}
        if extra_data:
            extra['extra_data'] = extra_data
        
        self.logger.log(level, message, extra=extra, exc_info=exc_info)
    
    def log_exception(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log exception with full traceback."""
        self.error(message, extra_data, exc_info=True)
    
    def log_function_call(self, func_name: str, args: tuple = (), kwargs: Dict[str, Any] = None, result: Any = None) -> None:
        """Log function call details."""
        extra_data = {
            'function': func_name,
            'args': str(args)[:200],  # Truncate long args
            'kwargs': str(kwargs or {})[:200],
            'result_type': type(result).__name__ if result is not None else 'None'
        }
        self.debug(f"Function call: {func_name}", extra_data)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return self.performance.get_stats()
    
    def reset_performance_stats(self) -> None:
        """Reset performance statistics."""
        self.performance.reset_stats()

class LoggerManager:
    """Manager for multiple loggers."""
    
    def __init__(self):
        self._loggers: Dict[str, ClickUpBrainLogger] = {}
        self._default_config = {
            'level': 'INFO',
            'log_file': ROOT / 'logs' / 'clickup_brain.log',
            'max_file_size': 10 * 1024 * 1024,
            'backup_count': 5,
            'console_output': True,
            'use_json': False
        }
    
    def get_logger(self, name: str, **kwargs) -> ClickUpBrainLogger:
        """Get or create a logger."""
        if name not in self._loggers:
            config = self._default_config.copy()
            config.update(kwargs)
            self._loggers[name] = ClickUpBrainLogger(name=name, **config)
        return self._loggers[name]
    
    def set_default_config(self, **kwargs) -> None:
        """Set default configuration for new loggers."""
        self._default_config.update(kwargs)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance stats from all loggers."""
        return {name: logger.get_performance_stats() for name, logger in self._loggers.items()}

# Global logger manager
logger_manager = LoggerManager()

def get_logger(name: str = "clickup_brain", **kwargs) -> ClickUpBrainLogger:
    """Get a logger instance."""
    return logger_manager.get_logger(name, **kwargs)

def setup_logging(level: str = "INFO", 
                  log_file: Optional[Path] = None,
                  console_output: bool = True,
                  use_json: bool = False) -> ClickUpBrainLogger:
    """Setup main logging system."""
    return logger_manager.get_logger(
        "clickup_brain",
        level=level,
        log_file=log_file,
        console_output=console_output,
        use_json=use_json
    )

@contextmanager
def log_performance(operation: str, logger: Optional[ClickUpBrainLogger] = None, extra_data: Optional[Dict[str, Any]] = None):
    """Context manager for performance logging."""
    if logger is None:
        logger = get_logger()
    
    with logger.performance.timer(operation, extra_data):
        yield

def log_function_calls(func):
    """Decorator to log function calls."""
    def wrapper(*args, **kwargs):
        logger = get_logger()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.log_function_call(
                func.__name__,
                args=args,
                kwargs=kwargs,
                result=result
            )
            
            logger.debug(f"Function {func.__name__} completed in {duration:.3f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.log_exception(f"Function {func.__name__} failed after {duration:.3f}s", {
                'function': func.__name__,
                'duration': duration,
                'error': str(e)
            })
            raise
    
    return wrapper

if __name__ == "__main__":
    # Demo logging system
    print("ClickUp Brain Logging System Demo")
    print("=" * 50)
    
    # Setup logging
    logger = setup_logging(level="DEBUG", console_output=True)
    
    # Test different log levels
    logger.debug("This is a debug message", {"test": "debug"})
    logger.info("This is an info message", {"test": "info"})
    logger.warning("This is a warning message", {"test": "warning"})
    logger.error("This is an error message", {"test": "error"})
    
    # Test performance logging
    with log_performance("demo_operation", logger, {"demo": True}):
        time.sleep(0.1)
        logger.info("Operation in progress")
    
    # Test function call logging
    @log_function_calls
    def demo_function(x: int, y: str = "test") -> str:
        return f"Result: {x} + {y}"
    
    result = demo_function(42, y="demo")
    logger.info(f"Function result: {result}")
    
    # Test exception logging
    try:
        raise ValueError("Demo exception")
    except Exception:
        logger.log_exception("Caught demo exception")
    
    # Show performance stats
    stats = logger.get_performance_stats()
    print(f"\nPerformance Stats: {stats}")
    
    print("\nLogging system demo completed!")







