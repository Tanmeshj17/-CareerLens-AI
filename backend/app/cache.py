"""
CareerLens AI — In-Memory Cache (Pre-Phase 8.7)
TTL-based cache with simple invalidation API.
"""
import time
import threading
from typing import Any, Optional, Callable

_cache: dict = {}
_lock = threading.Lock()

def get(key: str) -> Optional[Any]:
    with _lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at and time.time() > expires_at:
            del _cache[key]
            return None
        return value

def set(key: str, value: Any, ttl_seconds: int = 300):
    with _lock:
        _cache[key] = (value, time.time() + ttl_seconds)

def delete(key: str):
    with _lock:
        _cache.pop(key, None)

def invalidate_prefix(prefix: str):
    """Invalidate all cache keys starting with prefix."""
    with _lock:
        to_delete = [k for k in _cache if k.startswith(prefix)]
        for k in to_delete:
            del _cache[k]

def cached(key: str, ttl_seconds: int = 300):
    """Decorator for caching function results."""
    def decorator(fn: Callable):
        def wrapper(*args, **kwargs):
            cached_val = get(key)
            if cached_val is not None:
                return cached_val
            result = fn(*args, **kwargs)
            set(key, result, ttl_seconds)
            return result
        return wrapper
    return decorator

def get_or_compute(key: str, fn: Callable, ttl_seconds: int = 300) -> Any:
    """Get from cache or compute + cache."""
    cached_val = get(key)
    if cached_val is not None:
        return cached_val
    result = fn()
    set(key, result, ttl_seconds)
    return result

def stats() -> dict:
    with _lock:
        now = time.time()
        valid = sum(1 for v, exp in _cache.values() if not exp or exp > now)
        expired = len(_cache) - valid
        return {"total_keys": len(_cache), "valid": valid, "expired": expired}
