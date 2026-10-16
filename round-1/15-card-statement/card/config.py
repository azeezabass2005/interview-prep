from decimal import Decimal

APR = {"purchase": Decimal("0.24"), "cash": Decimal("0.29")}
CASH_FEE_RATE = Decimal("0.05")
CASH_FEE_MIN = Decimal("10.00")
LATE_FEE = Decimal("30.00")
OVER_LIMIT_FEE = Decimal("25.00")
MIN_PAYMENT_FLOOR = Decimal("25.00")
MIN_PAYMENT_RATE = Decimal("0.01")
DUE_DAYS = 21
DAYS_PER_YEAR = 365
