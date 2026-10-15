"""Tournament structure. Money is integer cents."""
ENTRY_FEE_CENTS = 5500
RAKE_PERCENT = 10
GUARANTEE_CENTS = 200_000

# (max entries for this bracket, percentages by place). None = no upper limit.
PAYOUT_TABLE = [
    (10, [65, 35]),
    (30, [50, 30, 20]),
    (None, [40, 25, 15, 12, 8]),
]
