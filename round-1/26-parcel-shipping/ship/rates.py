from decimal import Decimal as D

ZONE_RATES = {
    1: (D("5.00"), D("0.50")), 2: (D("5.00"), D("0.50")),
    3: (D("7.00"), D("0.80")), 4: (D("7.00"), D("0.80")),
    5: (D("9.00"), D("1.10")), 6: (D("9.00"), D("1.10")),
    7: (D("12.00"), D("1.60")), 8: (D("12.00"), D("1.60")),
}
DIM_DIVISOR = D("139")
OVERSIZE_LENGTH = D("48")
OVERSIZE_FEE = D("15.00")
FUEL_RATE = D("0.12")
RESIDENTIAL_FEE = D("4.50")
FREE_SHIPPING_THRESHOLD = D("75.00")
FREE_SHIPPING_MAX_ZONE = 4
