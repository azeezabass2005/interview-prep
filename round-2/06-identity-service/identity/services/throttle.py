from datetime import timedelta

from ..config import FAILED_LOGIN_WINDOW_MINUTES, MAX_FAILED_LOGINS


class LoginThrottle:
    """Locks an account after too many failed logins within a window (protects against password guessing)."""

    def __init__(self, clock):
        self._clock = clock
        self._failures: dict[str, list] = {}

    def _recent(self, key: str) -> list:
        cutoff = self._clock.now() - timedelta(minutes=FAILED_LOGIN_WINDOW_MINUTES)
        recent = [t for t in self._failures.get(key, []) if t > cutoff]
        self._failures[key] = recent
        return recent

    def locked(self, key: str) -> bool:
        return len(self._recent(key)) >= MAX_FAILED_LOGINS

    def failed(self, key: str) -> None:
        self._recent(key).append(self._clock.now())

    def succeeded(self, key: str) -> None:
        self._failures.pop(key, None)
