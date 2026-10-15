from decimal import Decimal
from typing import Dict, List

from .models import Item
from .policy import LATE_PENALTY_PER_DAY, LETTERS, MAX_LATE_DAYS, WEIGHTS

HUNDRED = Decimal(100)


def adjusted_points(item: Item) -> Decimal:
    points = item.points if item.points is not None else Decimal(0)
    if item.category == "homework" and item.days_late > 0:
        days = int(item.days_late)
        if days > MAX_LATE_DAYS:
            return Decimal(0)
        points = max(Decimal(0), points - item.max_points * LATE_PENALTY_PER_DAY * days)
    return points


def category_percent(items: List[Item], category: str) -> Decimal:
    rows = [(adjusted_points(i), i.max_points) for i in items if i.category == category]
    if not rows:
        raise ValueError(f"no graded items in {category}")
    if category == "homework" and len(rows) >= 2:
        rows.remove(min(rows, key=lambda r: r[0]))
    if category == "quiz":
        return sum(p / m * HUNDRED for p, m in rows) / len(rows)
    return sum(p for p, _ in rows) / sum(m for _, m in rows) * HUNDRED


def course_percent(items: List[Item]) -> Decimal:
    pct: Dict[str, Decimal] = {c: category_percent(items, c) for c in WEIGHTS}
    if pct["midterm"] > pct["final"]:
        pct["final"] = pct["midterm"]
    return sum(pct[c] * w for c, w in WEIGHTS.items())


def letter_for(percent: Decimal) -> str:
    for cutoff, letter in LETTERS:
        if percent >= cutoff:
            return letter
    return "F"


def final_letter(items: List[Item]) -> str:
    return letter_for(course_percent(items))
