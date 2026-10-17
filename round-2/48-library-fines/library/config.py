from decimal import Decimal

LOAN_DAYS = {"BOOK": 21, "DVD": 7}
DAILY_FINE = {"BOOK": Decimal("0.25"), "DVD": Decimal("1.00")}
MAX_FINE = {"BOOK": Decimal("20.00"), "DVD": Decimal("25.00")}
BOOK_GRACE_DAYS = 1
MAX_RENEWALS = 2
MAX_ITEMS = 10
BLOCK_AT = Decimal("10.00")
