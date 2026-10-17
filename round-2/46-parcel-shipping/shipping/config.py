from decimal import Decimal as D

CARRIERS = {
    "SPEEDY": {
        "divisor": D("139"), "fuel": D("0.12"), "transit_days": 2,
        "zones": {1: (D("5.00"), D("0.50")), 2: (D("5.00"), D("0.50")), 3: (D("7.00"), D("0.80")), 4: (D("7.00"), D("0.80")),
                  5: (D("9.00"), D("1.10")), 6: (D("9.00"), D("1.10")), 7: (D("12.00"), D("1.60")), 8: (D("12.00"), D("1.60"))},
    },
    "VALUE": {
        "divisor": D("166"), "fuel": D("0.09"), "transit_days": 4,
        "zones": {1: (D("4.50"), D("0.45")), 2: (D("4.50"), D("0.45")), 3: (D("6.25"), D("0.75")), 4: (D("6.25"), D("0.75")),
                  5: (D("8.50"), D("1.05")), 6: (D("8.50"), D("1.05")), 7: (D("11.00"), D("1.50")), 8: (D("11.00"), D("1.50"))},
    },
}
PREFERRED = "SPEEDY"
OVERSIZE_INCHES = D("48")
OVERSIZE_FEE = D("15.00")
RESIDENTIAL_FEE = D("4.50")
FREE_THRESHOLD = D("75.00")
FREE_MAX_ZONE = 4
CUTOFF_HOUR = 14
