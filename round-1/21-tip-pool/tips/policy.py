from decimal import Decimal

ROLE_POINTS = {
    "SERVER": 10,
    "BARTENDER": 8,
    "BUSSER": 5,
    "HOST": 3,
    "KITCHEN": 2,
    "MANAGER": 0,
}
INELIGIBLE_ROLES = {"MANAGER"}
CARD_FEE_RATE = Decimal("0.03")
MIN_HOURS = Decimal("2")
