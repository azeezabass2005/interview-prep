from ..config import BACKOFF_BASE_SECONDS, BACKOFF_CAP_SECONDS


def retry_delay_seconds(attempt: int) -> int:
    return BACKOFF_BASE_SECONDS * 2 * attempt
