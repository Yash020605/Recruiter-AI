import redis
import os

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=1.0, socket_connect_timeout=1.0)

def record_metric(name: str, duration: float):
    """Records the duration and increments the count for a metric name."""
    try:
        r.incrbyfloat(f"metrics:{name}:total_time", duration)
        r.incr(f"metrics:{name}:count")
    except Exception:
        pass

def get_average_metric(name: str) -> float:
    try:
        total = r.get(f"metrics:{name}:total_time")
        count = r.get(f"metrics:{name}:count")
        if total and count and int(count) > 0:
            return round(float(total) / int(count), 3)
    except Exception:
        pass
    return 0.0

def increment_counter(name: str, amount: int = 1):
    try:
        r.incrby(f"metrics:{name}", amount)
    except Exception:
        pass

def get_counter(name: str) -> int:
    try:
        val = r.get(f"metrics:{name}")
        return int(val) if val else 0
    except Exception:
        return 0
