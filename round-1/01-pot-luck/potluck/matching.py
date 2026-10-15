def count_matches(entry_code: str, winning_code: str) -> int:
    """Return how many digits of the entry's code match the winning code."""
    return sum(1 for digit in entry_code if digit in winning_code)
