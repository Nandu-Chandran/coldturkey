import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry(attempts=3, backoff_seconds=1, allowed_exceptions=(Exception,)):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, attempts + 1):
                try:
                    logger.debug(f"[Retry] Attempt {attempt}/{attempts} for {func.__name__}")
                    result = func(*args, **kwargs)
                    logger.debug(f"[Retry] Success on attempt {attempt} for {func.__name__}")
                    return result
                except allowed_exceptions as e:
                    last_exc = e
                    logger.warning(f"[Retry] Attempt {attempt} failed for {func.__name__}: {e!r}")
                    if attempt < attempts:
                        sleep = backoff_seconds * attempt
                        logger.info(f"[Retry] Sleeping {sleep}s before next attempt")
                        time.sleep(sleep)
            logger.error(f"[Retry] All {attempts} attempts failed for {func.__name__}")
            raise last_exc
        return wrapper
    return deco

