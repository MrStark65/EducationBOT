import asyncio
from typing import Callable, Any, Tuple
from dataclasses import dataclass


@dataclass
class RetryConfig:
    """Retry configuration"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0


async def retry_with_backoff(
    func: Callable,
    config: RetryConfig = None,
    error_types: Tuple = (Exception,)
) -> Any:
    """
    Execute function with exponential backoff retry
    
    Args:
        func: Async function to execute
        config: Retry configuration
        error_types: Tuple of exception types to catch
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries fail
    """
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            return await func()
        except error_types as e:
            last_exception = e
            if attempt == config.max_attempts - 1:
                raise
            
            # Calculate delay with exponential backoff
            delay = min(
                config.base_delay * (config.exponential_base ** attempt),
                config.max_delay
            )
            await asyncio.sleep(delay)
    
    if last_exception:
        raise last_exception
