import random


def bucket(flag_key: str, user_id: str) -> int:
    """The user's rollout bucket, 0-99."""
    return random.randrange(100)
