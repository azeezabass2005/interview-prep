from decimal import Decimal

ROOM_TYPES = {"STANDARD": (10, Decimal("150")), "DELUXE": (5, Decimal("220")), "SUITE": (2, Decimal("400"))}
WEEKEND_SURCHARGE = Decimal("0.20")
LOS_TIERS = [(7, Decimal("0.15")), (3, Decimal("0.05"))]
NON_REFUNDABLE_DISCOUNT = Decimal("0.10")
PROMOS = {"SAVE50": Decimal("50")}
TAX_RATE = Decimal("0.1475")
CITY_FEE = Decimal("3.50")
CHECK_IN_HOUR = 15
FULL_REFUND_HOURS = 168
PARTIAL_REFUND_HOURS = 48
