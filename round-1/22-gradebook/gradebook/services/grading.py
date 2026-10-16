from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from ..config import LETTERS, WEIGHTS
from ..models import Course
from .late import penalised

HUNDRED = Decimal(100)


def scored_items(course: Course, student: str, category: str) -> List[Tuple[Decimal, Decimal]]:
    rows = []
    for a in course.assignments.values():
        if a.category != category:
            continue
        sub = course.submissions.get((student, a.assignment_id))
        if sub is None or sub.points is None:
            rows.append((Decimal(0), a.max_points))
        else:
            rows.append((penalised(a, sub.points, sub.submitted_at), a.max_points))
    return rows


def category_percent(course: Course, student: str, category: str) -> Optional[Decimal]:
    rows = scored_items(course, student, category)
    if not rows:
        return None
    if category == "HOMEWORK" and len(rows) >= 2:
        rows.remove(min(rows, key=lambda r: r[0]))
    if category == "QUIZ":
        return sum(p / m * HUNDRED for p, m in rows) / len(rows)
    return sum(p for p, _ in rows) / sum(m for _, m in rows) * HUNDRED


def course_percent(course: Course, student: str) -> Decimal:
    pct: Dict[str, Optional[Decimal]] = {c: category_percent(course, student, c) for c in WEIGHTS}
    if pct["MIDTERM"] is not None and pct["FINAL"] is not None and pct["MIDTERM"] > pct["FINAL"]:
        pct["FINAL"] = pct["MIDTERM"]
    return sum(((pct[c] or Decimal(0)) * w for c, w in WEIGHTS.items()), Decimal(0))


def letter(percent: Decimal) -> str:
    for cutoff, grade in LETTERS:
        if percent >= cutoff:
            return grade
    return "F"
