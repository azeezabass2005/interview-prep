from decimal import Decimal

BASE = Decimal("2.50")
PER_MILE = Decimal("1.20")
PER_MINUTE = Decimal("0.30")
BOOKING_FEE = Decimal("2.00")
MINIMUM = Decimal("7.00")
SURGE_CAP = Decimal("3.0")
FREE_WAIT_MINUTES = 2
WAIT_PER_MINUTE = Decimal("0.40")
PROMO_MAX = Decimal("10.00")
CANCEL_FEE = Decimal("5.00")
CANCEL_FREE_SECONDS = 120
DRIVER_LATE_GRACE_SECONDS = 300
DRIVER_SHARE = Decimal("0.75")
PROMOS = {"SPRING20": Decimal("0.20"), "HALFOFF": Decimal("0.50")}
