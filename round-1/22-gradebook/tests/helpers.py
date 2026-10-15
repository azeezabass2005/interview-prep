from decimal import Decimal as D

from grades.models import Item


def item(category, name, points, max_points, days_late=0, excused=False):
    pts = None if points is None else D(str(points))
    return Item(category, name, pts, D(str(max_points)), D(str(days_late)), excused)


def full_marks_except(**overrides):
    """A complete gradebook at 100% everywhere unless overridden by category -> list of items."""
    base = {
        "homework": [item("homework", "hw1", 10, 10), item("homework", "hw2", 10, 10)],
        "quiz": [item("quiz", "q1", 10, 10)],
        "midterm": [item("midterm", "mid", 100, 100)],
        "final": [item("final", "fin", 100, 100)],
    }
    base.update(overrides)
    return [i for items in base.values() for i in items]
