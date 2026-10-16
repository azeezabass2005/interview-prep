from datetime import timedelta
from decimal import Decimal

MAX_WAITLIST = 10
LATE_WINDOW = timedelta(hours=12)
PROMOTION_CUTOFF = timedelta(hours=1)
LATE_FEE = Decimal("10.00")
PLANS = ("UNLIMITED", "PREMIUM", "PACK")
