"""
Structured Logging Configuration for Ultimate Launch Planning System
Provides comprehensive logging with different levels and outputs
"""

import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
import traceback

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)

class LaunchPlanningLogger:
    """Main logging configuration class"""
    
    def __init__(self, 
                 log_level: str = "INFO",
                 log_file: Optional[str] = None,
                 json_logs: bool = False,
                 console_output: bool = True):
        
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_file = log_file
        self.json_logs = json_logs
        self.console_output = console_output
        
        # Create logs directory if it doesn't exist
        if self.log_file:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            if self.json_logs:
                console_handler.setFormatter(JSONFormatter())
            else:
                console_formatter = ColoredFormatter(
                    '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # File handler
        if self.log_file:
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            
            if self.json_logs:
                file_handler.setFormatter(JSONFormatter())
            else:
                file_formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)-20s | %(module)s:%(funcName)s:%(lineno)d | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)
            
            root_logger.addHandler(file_handler)
        
        # Set specific logger levels
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance with the given name"""
        return logging.getLogger(name)
    
    def log_launch_event(self, 
                        logger: logging.Logger,
                        event_type: str,
                        phase: str,
                        details: Dict[str, Any]):
        """Log a launch planning event with structured data"""
        extra_fields = {
            "event_type": event_type,
            "launch_phase": phase,
            "details": details
        }
        
        logger.info(f"Launch Event: {event_type} in {phase}", 
                   extra={'extra_fields': extra_fields})
    
    def log_performance_metric(self,
                              logger: logging.Logger,
                              metric_name: str,
                              value: float,
                              unit: str = "",
                              context: Dict[str, Any] = None):
        """Log performance metrics"""
        extra_fields = {
            "metric_name": metric_name,
            "metric_value": value,
            "metric_unit": unit,
            "context": context or {}
        }
        
        logger.info(f"Performance Metric: {metric_name} = {value} {unit}",
                   extra={'extra_fields': extra_fields})
    
    def log_error_with_context(self,
                              logger: logging.Logger,
                              error: Exception,
                              context: Dict[str, Any] = None):
        """Log errors with additional context"""
        extra_fields = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        logger.error(f"Error: {type(error).__name__}: {str(error)}",
                    exc_info=True,
                    extra={'extra_fields': extra_fields})

# Global logger instance
_logger_config = None

def setup_logging(log_level: str = "INFO",
                 log_file: Optional[str] = None,
                 json_logs: bool = False,
                 console_output: bool = True) -> LaunchPlanningLogger:
    """Setup global logging configuration"""
    global _logger_config
    _logger_config = LaunchPlanningLogger(
        log_level=log_level,
        log_file=log_file,
        json_logs=json_logs,
        console_output=console_output
    )
    return _logger_config

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    if _logger_config is None:
        setup_logging()
    return _logger_config.get_logger(name)

def log_launch_event(event_type: str,
                    phase: str,
                    details: Dict[str, Any],
                    logger_name: str = "launch_planning"):
    """Convenience function to log launch events"""
    logger = get_logger(logger_name)
    if _logger_config:
        _logger_config.log_launch_event(logger, event_type, phase, details)

def log_performance_metric(metric_name: str,
                          value: float,
                          unit: str = "",
                          context: Dict[str, Any] = None,
                          logger_name: str = "performance"):
    """Convenience function to log performance metrics"""
    logger = get_logger(logger_name)
    if _logger_config:
        _logger_config.log_performance_metric(logger, metric_name, value, unit, context)

def log_error_with_context(error: Exception,
                          context: Dict[str, Any] = None,
                          logger_name: str = "error_handler"):
    """Convenience function to log errors with context"""
    logger = get_logger(logger_name)
    if _logger_config:
        _logger_config.log_error_with_context(logger, error, context)

# Example usage
if __name__ == "__main__":
    # Setup logging
    setup_logging(
        log_level="DEBUG",
        log_file="logs/launch_planning.log",
        json_logs=False,
        console_output=True
    )
    
    # Get loggers
    main_logger = get_logger("main")
    perf_logger = get_logger("performance")
    
    # Test logging
    main_logger.info("Starting Ultimate Launch Planning System")
    
    # Log a launch event
    log_launch_event(
        event_type="phase_start",
        phase="pre_launch",
        details={"tasks_completed": 5, "total_tasks": 10}
    )
    
    # Log performance metrics
    log_performance_metric(
        metric_name="execution_time",
        value=1.234,
        unit="seconds",
        context={"operation": "data_processing"}
    )
    
    # Test error logging
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        log_error_with_context(
            error=e,
            context={"operation": "test", "user_id": "test_user"}
        )
    
    main_logger.info("Logging system test completed")








