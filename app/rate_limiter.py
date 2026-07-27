"""
Rate Limiter module to protect auth endpoints (e.g., login) from brute-force attacks.
"""
import time
from typing import Dict, Tuple
from fastapi import HTTPException, status


class LoginRateLimiter:
    """In-memory rate limiter tracking failed attempts per identifier (email or IP address)."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: Dict[str, Tuple[int, float]] = {}

    def check_rate_limit(self, key: str) -> None:
        """Check if key has exceeded allowed failed attempts within window."""
        now = time.time()
        if key in self._attempts:
            count, reset_time = self._attempts[key]
            if now > reset_time:
                # Window has passed, reset count
                self._attempts[key] = (0, now + self.window_seconds)
            elif count >= self.max_attempts:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many failed login attempts. Please try again later.",
                )

    def record_failure(self, key: str) -> None:
        """Record a failed login attempt for key."""
        now = time.time()
        if key in self._attempts:
            count, reset_time = self._attempts[key]
            if now > reset_time:
                self._attempts[key] = (1, now + self.window_seconds)
            else:
                self._attempts[key] = (count + 1, reset_time)
        else:
            self._attempts[key] = (1, now + self.window_seconds)

    def record_success(self, key: str) -> None:
        """Clear failed attempt history on successful authentication."""
        if key in self._attempts:
            del self._attempts[key]


login_limiter = LoginRateLimiter(max_attempts=5, window_seconds=60)
