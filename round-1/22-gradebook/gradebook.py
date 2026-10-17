from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

WEIGHTS = {"HOMEWORK": Decimal("0.30"), "QUIZ": Decimal("0.20"), "EXAM": Decimal("0.50")}
LATE_PENALTY = Decimal("0.10")
MAX_LATE_DAYS = 5
LETTERS = [(Decimal("90"), "A"), (Decimal("80"), "B"), (Decimal("70"), "C"), (Decimal("60"), "D")]
HUNDREDTH = Decimal("0.01")


class GradeError(Exception):
    pass


@dataclass
class Assignment:
    assignment_id: str
    category: str
    possible: Decimal
    due: datetime


class Gradebook:
    def __init__(self):
        self.assignments = {}
        self.submissions = {}
        self.excused = set()

    def add_assignment(self, assignment_id, category, possible, due):
        if category not in WEIGHTS:
            raise GradeError("unknown category")
        self.assignments[assignment_id] = Assignment(assignment_id, category, Decimal(str(possible)), due)

    def submit(self, assignment_id, student, score, at):
        if assignment_id not in self.assignments:
            raise GradeError("unknown assignment")
        self.submissions[(assignment_id, student)] = (Decimal(str(score)), at)

    def excuse(self, assignment_id, student):
        self.excused.add((assignment_id, student))

    def _earned(self, a, score, at):
        if at <= a.due:
            return score
        days_late = (at - a.due) // timedelta(days=1)
        if days_late > MAX_LATE_DAYS:
            return Decimal("0")
        return max(Decimal("0"), score - a.possible * LATE_PENALTY * days_late)

    def _items(self, student, category, as_of):
        items = []
        for a in self.assignments.values():
            if a.category != category:
                continue
            if (a.assignment_id, student) in self.excused:
                items.append((Decimal("0"), a.possible))
                continue
            submission = self.submissions.get((a.assignment_id, student))
            if submission:
                items.append((self._earned(a, *submission), a.possible))
            elif as_of > a.due:
                items.append((Decimal("0"), a.possible))
        if category == "HOMEWORK" and len(items) >= 2:
            items.remove(min(items, key=lambda i: i[0]))
        return items

    def category_percent(self, student, category, as_of):
        items = self._items(student, category, as_of)
        if not items:
            return None
        earned = sum(e for e, _ in items)
        possible = sum(p for _, p in items)
        return (earned / possible * 100).quantize(HUNDREDTH, rounding=ROUND_HALF_UP)

    def final(self, student, as_of):
        total, weights = Decimal("0"), sum(WEIGHTS.values())
        for category, weight in WEIGHTS.items():
            pct = self.category_percent(student, category, as_of)
            if pct is not None:
                total += weight * pct
        percent = (total / weights).quantize(HUNDREDTH, rounding=ROUND_HALF_UP)
        letter = next((l for cut, l in LETTERS if percent > cut), "F")
        return percent, letter
