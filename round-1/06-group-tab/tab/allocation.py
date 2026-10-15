from typing import Dict, Iterable


def split_evenly(amount: int, people: Iterable[str]) -> Dict[str, int]:
    """Split cents evenly; leftover cents go one each in alphabetical order."""
    names = sorted(people)
    base, leftover = divmod(amount, len(names))
    return {name: base + (1 if i < leftover else 0) for i, name in enumerate(names)}


def allocate_proportionally(amount: int, weights: Dict[str, int]) -> Dict[str, int]:
    """Split cents in proportion to weights."""
    total_weight = sum(weights.values())
    if total_weight == 0:
        return split_evenly(amount, weights)
    return {name: amount * weight // total_weight for name, weight in weights.items()}
