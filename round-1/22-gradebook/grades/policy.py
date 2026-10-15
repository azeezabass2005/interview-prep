from decimal import Decimal

WEIGHTS = {
    "homework": Decimal("0.30"),
    "quiz": Decimal("0.20"),
    "midterm": Decimal("0.20"),
    "final": Decimal("0.30"),
}
LATE_PENALTY_PER_DAY = Decimal("0.10")
MAX_LATE_DAYS = 3
LETTERS = [(Decimal(90), "A"), (Decimal(80), "B"), (Decimal(70), "C"), (Decimal(60), "D")]
