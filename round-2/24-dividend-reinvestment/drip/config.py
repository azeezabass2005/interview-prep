from decimal import Decimal

WITHHOLDING_RATES = {"US": Decimal("0"), "GB": Decimal("0.15"), "JP": Decimal("0.10")}
DEFAULT_WITHHOLDING_RATE = Decimal("0.30")
REINVEST_FEE = Decimal("0.50")
FEE_CAP_RATE = Decimal("0.05")
CENT = Decimal("0.01")
SHARE_UNIT = Decimal("0.0001")
