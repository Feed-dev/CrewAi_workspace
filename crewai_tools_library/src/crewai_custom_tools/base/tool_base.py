"""
Enhanced base classes for CrewAI tools following best practices.
"""

from typing import Any, Dict, Optional, Type
from abc import ABC, abstractmethod
import logging
from functools import wraps
from datetime import datetime, timedelta

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ToolError(Exception):
    """Custom exception for tool-related errors."""
    pass


class ToolValidationError(ToolError):
    """Exception for input validation errors."""
    pass


class ToolExecutionError(ToolError):
    """Exception for tool execution errors."""
    pass


def with_error_handling(func):
    """Decorator for consistent error handling across tools."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except ToolError:
            raise  # Re-raise tool-specific errors
        except Exception as e:
            self._log_error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise ToolExecutionError(f"Tool execution failed: {str(e)}")
    return wrapper


class EnhancedBaseTool(BaseTool, ABC):
    """
    Enhanced base class for CrewAI tools with additional features:
    - Consistent error handling
    - Input validation
    - Logging
    - Caching support
    - Performance metrics
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.execution_count = 0
        self.total_execution_time = 0.0
        self._cache = {}
        self._cache_ttl = timedelta(minutes=30)  # Default cache TTL
    
    def _log_info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(f"[{self.__class__.__name__}] {message}")
    
    def _log_error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(f"[{self.__class__.__name__}] {message}")
    
    def _log_warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(f"[{self.__class__.__name__}] {message}")
    
    def _validate_input(self, **kwargs) -> None:
        """
        Validate input parameters.
        Override in subclasses for custom validation.
        """
        pass
    
    def _should_cache(self, result: Any, **kwargs) -> bool:
        """
        Determine if result should be cached.
        Override in subclasses for custom caching logic.
        """
        return True
    
    def _get_cache_key(self, **kwargs) -> str:
        """Generate cache key from input parameters."""
        return str(sorted(kwargs.items()))
    
    def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached result if available and not expired."""
        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < self._cache_ttl:
                return result
            else:
                # Remove expired cache entry
                del self._cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: Any) -> None:
        """Cache the result with timestamp."""
        if self._should_cache(result):
            self._cache[cache_key] = (result, datetime.now())
    
    @abstractmethod
    def _execute(self, **kwargs) -> Any:
        """
        Core execution logic.
        Must be implemented by subclasses.
        """
        pass
    
    def _run(self, **kwargs) -> Any:
        """
        Main execution method with enhanced features.
        """
        start_time = datetime.now()
        
        try:
            # Input validation
            self._validate_input(**kwargs)
            
            # Check cache
            cache_key = self._get_cache_key(**kwargs)
            cached_result = self._get_cached_result(cache_key)
            if cached_result is not None:
                self._log_info(f"Returning cached result for key: {cache_key}")
                return cached_result
            
            # Execute tool logic
            self._log_info(f"Executing with parameters: {kwargs}")
            result = self._execute(**kwargs)
            
            # Cache result
            self._cache_result(cache_key, result)
            
            # Update metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.execution_count += 1
            self.total_execution_time += execution_time
            
            self._log_info(f"Execution completed in {execution_time:.2f}s")
            return result
            
        except ToolError:
            raise  # Re-raise tool-specific errors
        except Exception as e:
            self._log_error(f"Unexpected error: {str(e)}")
            raise ToolExecutionError(f"Tool execution failed: {str(e)}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this tool."""
        avg_time = (
            self.total_execution_time / self.execution_count 
            if self.execution_count > 0 else 0
        )
        return {
            "execution_count": self.execution_count,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": avg_time,
            "cache_entries": len(self._cache),
        }
    
    def clear_cache(self) -> None:
        """Clear the tool's cache."""
        self._cache.clear()
        self._log_info("Cache cleared")
    
    def set_cache_ttl(self, minutes: int) -> None:
        """Set cache time-to-live in minutes."""
        self._cache_ttl = timedelta(minutes=minutes)
        self._log_info(f"Cache TTL set to {minutes} minutes")


class BaseToolInput(BaseModel):
    """Base input schema with common validation."""
    
    class Config:
        extra = "forbid"  # Prevent extra fields
        str_strip_whitespace = True  # Auto-strip whitespace
    
    def validate_required_fields(self, required_fields: list) -> None:
        """Validate that required fields are present and not empty."""
        for field in required_fields:
            value = getattr(self, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ToolValidationError(f"Required field '{field}' is missing or empty")