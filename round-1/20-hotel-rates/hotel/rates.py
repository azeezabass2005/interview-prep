from decimal import Decimal

BASE_RATES = {"STANDARD": Decimal("150"), "DELUXE": Decimal("220"), "SUITE": Decimal("400")}
WEEKEND_SURCHARGE = Decimal("0.20")
LOS_SHORT = (3, Decimal("0.05"))
LOS_LONG = (7, Decimal("0.15"))
PROMOS = {"SAVE50": Decimal("50")}
TAX_RATE = Decimal("0.1475")
CITY_FEE_PER_NIGHT = Decimal("3.50")
CHECK_IN_HOUR = 15
FULL_REFUND_HOURS = 168
PARTIAL_REFUND_HOURS = 48
