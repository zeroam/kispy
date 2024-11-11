import threading
import time
from collections import deque
from datetime import datetime
from typing import Deque

from kispy.constants import RATE_LIMIT_PER_SECOND, RATE_LIMIT_WINDOW


class RateLimiter:
    """Thread-safe Rate Limiter implementation using sliding window."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, max_requests: int = RATE_LIMIT_PER_SECOND, window: float = RATE_LIMIT_WINDOW):
        if not hasattr(self, "initialized"):
            self.max_requests = max_requests
            self.window = window
            self._requests: Deque[float] = deque()
            self.initialized = True

    def configure(self, max_requests: int, window: float) -> None:
        self.max_requests = max_requests
        self.window = window
        self.clear()

    def wait_if_needed(self) -> None:
        """Wait if the rate limit would be exceeded by this request."""
        with self._lock:
            now = datetime.now().timestamp()
            self._clean_expired_requests(now)

            if len(self._requests) >= self.max_requests:
                sleep_time = self.window - (now - self._requests[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)

            self._requests.append(now)

    def _clean_expired_requests(self, now: float) -> None:
        """Remove expired requests."""
        cutoff_time = now - self.window
        while self._requests and self._requests[0] < cutoff_time:
            self._requests.popleft()

    def clear(self) -> None:
        """Clear all stored request history."""
        with self._lock:
            self._requests.clear()
