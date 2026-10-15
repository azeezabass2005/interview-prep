"""Fixed constants for the Pot Luck drawing. All money is in integer cents."""

SPONSOR_SEED_CENTS = 1_000_000  # $10,000
ENTRY_FEE_CENTS = 500  # $5 per entry
CODE_LENGTH = 5

# matches -> percentage of the pot
TIER_SHARES = {
    5: 100,
    4: 40,
    3: 20,
    2: 5,
    1: 0,
}
