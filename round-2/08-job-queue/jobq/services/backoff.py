from ..config import BACKOFF_BASE_SECONDS, BACKOFF_CAP_SECONDS


def retry_delay_seconds(attempt: int) -> int:
    """Delay before the next try, after `attempt` failed attempts (attempt >= 1)."""
    return BACKOFF_BASE_SECONDS * 2 * attempt
