from decimal import Decimal

HAIRCUTS = {"EQUITY": Decimal("0.25"), "ETF": Decimal("0.15"), "BOND": Decimal("0.10")}
CONCENTRATION_LIMIT = Decimal("0.40")
CONCENTRATED_HAIRCUT = Decimal("0.50")
STALE_SURCHARGE = Decimal("0.10")
SHORT_ADD_ON = Decimal("0.30")
CALL_ROUNDING = Decimal("100")
