#!/usr/bin/env python3
"""
ClickUp Brain Error Handling System
==================================

Comprehensive error handling, recovery mechanisms, and graceful degradation.
"""

import sys
import traceback
import functools
import asyncio
from typing import Any, Callable, Dict, Optional, Union, Type, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path

ROOT = Path(__file__).parent

class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories."""
    SYSTEM = "system"
    NETWORK = "network"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    ML = "ml"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"

@dataclass
class ErrorContext:
    """Context information for errors."""
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    environment: Optional[str] = None

@dataclass
class ErrorInfo:
    """Structured error information."""
    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    traceback: Optional[str] = None
    recovery_action: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_after: Optional[timedelta] = None

class ClickUpBrainError(Exception):
    """Base exception for ClickUp Brain system."""
    
    def __init__(self, 
                 message: str,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 context: Optional[ErrorContext] = None,
                 recovery_action: Optional[str] = None,
                 retry_count: int = 0,
                 max_retries: int = 3,
                 retry_after: Optional[timedelta] = None):
        
        super().__init__(message)
        self.severity = severity
        self.category = category
        self.context = context or ErrorContext(timestamp=datetime.now())
        self.recovery_action = recovery_action
        self.retry_count = retry_count
        self.max_retries = max_retries
        self.retry_after = retry_after
    
    def to_error_info(self) -> ErrorInfo:
        """Convert to ErrorInfo structure."""
        return ErrorInfo(
            error_type=self.__class__.__name__,
            error_message=str(self),
            severity=self.severity,
            category=self.category,
            context=self.context,
            traceback=traceback.format_exc(),
            recovery_action=self.recovery_action,
            retry_count=self.retry_count,
            max_retries=self.max_retries,
            retry_after=self.retry_after
        )

class SystemError(ClickUpBrainError):
    """System-level errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.SYSTEM, **kwargs)

class NetworkError(ClickUpBrainError):
    """Network-related errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorSeverity.MEDIUM, ErrorCategory.NETWORK, **kwargs)

class DatabaseError(ClickUpBrainError):
    """Database-related errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.DATABASE, **kwargs)

class AuthenticationError(ClickUpBrainError):
    """Authentication-related errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.AUTHENTICATION, **kwargs)

class ValidationError(ClickUpBrainError):
    """Validation errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorSeverity.LOW, ErrorCategory.VALIDATION, **kwargs)

class IntegrationError(ClickUpBrainError):
    """External integration errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorSeverity.MEDIUM, ErrorCategory.INTEGRATION, **kwargs)

class MLError(ClickUpBrainError):
    """Machine learning errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorSeverity.MEDIUM, ErrorCategory.ML, **kwargs)

class ConfigurationError(ClickUpBrainError):
    """Configuration errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.CONFIGURATION, **kwargs)

class ErrorHandler:
    """Main error handling system."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_history: Dict[str, list] = {}
        self.circuit_breakers: Dict[str, Dict] = {}
        self.retry_strategies: Dict[Type[Exception], Dict] = {}
        self._setup_default_retry_strategies()
    
    def _setup_default_retry_strategies(self) -> None:
        """Setup default retry strategies for common exceptions."""
        self.retry_strategies.update({
            NetworkError: {
                'max_retries': 3,
                'backoff_factor': 2,
                'retry_after': timedelta(seconds=1)
            },
            DatabaseError: {
                'max_retries': 2,
                'backoff_factor': 1.5,
                'retry_after': timedelta(seconds=2)
            },
            IntegrationError: {
                'max_retries': 3,
                'backoff_factor': 2,
                'retry_after': timedelta(seconds=1)
            }
        })
    
    def handle_error(self, 
                    error: Exception,
                    context: Optional[ErrorContext] = None,
                    recovery_callback: Optional[Callable] = None) -> Any:
        """Handle an error with appropriate recovery actions."""
        
        # Convert to ClickUpBrainError if needed
        if not isinstance(error, ClickUpBrainError):
            error = SystemError(str(error), context=context)
        
        error_info = error.to_error_info()
        
        # Log the error
        self._log_error(error_info)
        
        # Store in history
        self._store_error_history(error_info)
        
        # Check circuit breaker
        if self._is_circuit_open(error_info):
            raise SystemError("Circuit breaker is open", context=context)
        
        # Attempt recovery
        if recovery_callback and error_info.retry_count < error_info.max_retries:
            try:
                return self._attempt_recovery(error_info, recovery_callback)
            except Exception as recovery_error:
                self.logger.error(f"Recovery failed: {recovery_error}")
        
        # Re-raise if no recovery possible
        raise error
    
    def _log_error(self, error_info: ErrorInfo) -> None:
        """Log error information."""
        log_data = {
            'error_type': error_info.error_type,
            'error_message': error_info.error_message,
            'severity': error_info.severity.value,
            'category': error_info.category.value,
            'component': error_info.context.component,
            'operation': error_info.context.operation,
            'retry_count': error_info.retry_count,
            'recovery_action': error_info.recovery_action
        }
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"Critical error: {error_info.error_message}", extra=log_data)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(f"High severity error: {error_info.error_message}", extra=log_data)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"Medium severity error: {error_info.error_message}", extra=log_data)
        else:
            self.logger.info(f"Low severity error: {error_info.error_message}", extra=log_data)
    
    def _store_error_history(self, error_info: ErrorInfo) -> None:
        """Store error in history for analysis."""
        key = f"{error_info.category.value}:{error_info.context.component}"
        if key not in self.error_history:
            self.error_history[key] = []
        
        self.error_history[key].append(error_info)
        
        # Keep only recent errors (last 100 per category)
        if len(self.error_history[key]) > 100:
            self.error_history[key] = self.error_history[key][-100:]
    
    def _is_circuit_open(self, error_info: ErrorInfo) -> bool:
        """Check if circuit breaker is open for this error type."""
        key = f"{error_info.category.value}:{error_info.context.component}"
        
        if key not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[key]
        if datetime.now() < breaker['reset_time']:
            return True
        
        # Reset circuit breaker
        del self.circuit_breakers[key]
        return False
    
    def _attempt_recovery(self, error_info: ErrorInfo, recovery_callback: Callable) -> Any:
        """Attempt to recover from error."""
        if error_info.retry_after:
            import time
            time.sleep(error_info.retry_after.total_seconds())
        
        # Update retry count
        error_info.retry_count += 1
        
        self.logger.info(f"Attempting recovery (attempt {error_info.retry_count}/{error_info.max_retries})")
        
        return recovery_callback()
    
    def open_circuit_breaker(self, category: ErrorCategory, component: str, duration: timedelta = timedelta(minutes=5)) -> None:
        """Open circuit breaker for a component."""
        key = f"{category.value}:{component}"
        self.circuit_breakers[key] = {
            'reset_time': datetime.now() + duration
        }
        self.logger.warning(f"Circuit breaker opened for {key} until {self.circuit_breakers[key]['reset_time']}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        stats = {}
        for key, errors in self.error_history.items():
            stats[key] = {
                'total_errors': len(errors),
                'severity_breakdown': {
                    severity.value: sum(1 for e in errors if e.severity == severity)
                    for severity in ErrorSeverity
                },
                'recent_errors': len([e for e in errors if e.context.timestamp > datetime.now() - timedelta(hours=1)])
            }
        return stats

def error_handler(severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 max_retries: int = 3,
                 retry_after: Optional[timedelta] = None,
                 recovery_action: Optional[str] = None):
    """Decorator for error handling."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler = ErrorHandler()
            context = ErrorContext(
                timestamp=datetime.now(),
                component=func.__module__,
                operation=func.__name__
            )
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        # Final attempt failed
                        error = ClickUpBrainError(
                            str(e),
                            severity=severity,
                            category=category,
                            context=context,
                            recovery_action=recovery_action,
                            retry_count=attempt,
                            max_retries=max_retries,
                            retry_after=retry_after
                        )
                        handler.handle_error(error, context)
                        raise error
                    
                    # Wait before retry
                    if retry_after:
                        import time
                        time.sleep(retry_after.total_seconds())
        
        return wrapper
    return decorator

def async_error_handler(severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                       category: ErrorCategory = ErrorCategory.UNKNOWN,
                       max_retries: int = 3,
                       retry_after: Optional[timedelta] = None,
                       recovery_action: Optional[str] = None):
    """Decorator for async error handling."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            handler = ErrorHandler()
            context = ErrorContext(
                timestamp=datetime.now(),
                component=func.__module__,
                operation=func.__name__
            )
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        # Final attempt failed
                        error = ClickUpBrainError(
                            str(e),
                            severity=severity,
                            category=category,
                            context=context,
                            recovery_action=recovery_action,
                            retry_count=attempt,
                            max_retries=max_retries,
                            retry_after=retry_after
                        )
                        handler.handle_error(error, context)
                        raise error
                    
                    # Wait before retry
                    if retry_after:
                        await asyncio.sleep(retry_after.total_seconds())
        
        return wrapper
    return decorator

def graceful_degradation(fallback_value: Any = None, fallback_func: Optional[Callable] = None):
    """Decorator for graceful degradation."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = ErrorHandler()
                context = ErrorContext(
                    timestamp=datetime.now(),
                    component=func.__module__,
                    operation=func.__name__
                )
                
                error = ClickUpBrainError(
                    f"Graceful degradation triggered: {str(e)}",
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.SYSTEM,
                    context=context
                )
                handler.handle_error(error, context)
                
                if fallback_func:
                    return fallback_func(*args, **kwargs)
                return fallback_value
        
        return wrapper
    return decorator

# Global error handler instance
error_handler_instance = ErrorHandler()

def handle_error(error: Exception, context: Optional[ErrorContext] = None, recovery_callback: Optional[Callable] = None) -> Any:
    """Global error handling function."""
    return error_handler_instance.handle_error(error, context, recovery_callback)

if __name__ == "__main__":
    # Demo error handling system
    print("ClickUp Brain Error Handling System Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Test error handling decorator
    @error_handler(severity=ErrorSeverity.MEDIUM, category=ErrorCategory.NETWORK, max_retries=2)
    def unreliable_network_call():
        import random
        if random.random() < 0.7:  # 70% failure rate
            raise NetworkError("Network connection failed")
        return "Success!"
    
    # Test graceful degradation
    @graceful_degradation(fallback_value="Default response")
    def unreliable_service():
        import random
        if random.random() < 0.5:
            raise SystemError("Service unavailable")
        return "Service response"
    
    # Test multiple calls
    for i in range(5):
        try:
            result = unreliable_network_call()
            print(f"Network call {i+1}: {result}")
        except Exception as e:
            print(f"Network call {i+1}: Failed - {e}")
        
        result = unreliable_service()
        print(f"Service call {i+1}: {result}")
    
    # Show error stats
    stats = error_handler_instance.get_error_stats()
    print(f"\nError Statistics: {json.dumps(stats, indent=2, default=str)}")
    
    print("\nError handling system demo completed!")









