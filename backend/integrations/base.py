import httpx
from typing import Callable, Any
import functools
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class IntegrationException(Exception):
    """Base exception for integration errors."""
    pass

class RateLimitException(IntegrationException):
    """Raised when an API rate limit is exceeded (HTTP 429)."""
    pass

class AuthException(IntegrationException):
    """Raised when authentication fails (HTTP 401/403)."""
    pass

def handle_httpx_error(func: Callable) -> Callable:
    """Decorator to handle httpx errors and map them to custom exceptions."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error(f"Rate limit exceeded for {func.__name__}")
                raise RateLimitException(f"Rate limit exceeded: {e}")
            elif e.response.status_code in (401, 403):
                logger.error(f"Authentication failed for {func.__name__}")
                raise AuthException(f"Auth error: {e}")
            logger.error(f"HTTP Status Error in {func.__name__}: {e}")
            raise IntegrationException(f"API Error: {e}")
        except httpx.RequestError as e:
            logger.error(f"Request Error in {func.__name__}: {e}")
            raise IntegrationException(f"Request Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected Error in {func.__name__}: {e}")
            raise IntegrationException(f"Unexpected Error: {e}")
    return wrapper

def async_retry():
    """
    Retry logic for integrations.
    Retries on any IntegrationException (except AuthException, which indicates invalid credentials).
    Uses exponential backoff up to 3 attempts.
    """
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(IntegrationException) & ~retry_if_exception_type(AuthException),
        reraise=True
    )
