from decimal import Decimal

WEIGHTS = {"HOMEWORK": Decimal("0.30"), "QUIZ": Decimal("0.20"), "MIDTERM": Decimal("0.20"), "FINAL": Decimal("0.30")}
LATE_PENALTY_PER_DAY = Decimal("0.10")
MAX_LATE_DAYS = 3
LETTERS = [(Decimal(90), "A"), (Decimal(80), "B"), (Decimal(70), "C"), (Decimal(60), "D")]
