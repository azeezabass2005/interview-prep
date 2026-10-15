"""Service configuration. Values are defaults; ops can override them per environment."""

BATCH_SIZE = 5

WORKDAY_START_HOUR = 9
WORKDAY_END_HOUR = 18
SLOT_MINUTES = 30

MIN_DURATION_MINUTES = 15
MAX_DURATION_MINUTES = 120

INTERNAL_DOMAIN = "bloomberg.example"
VIP_SENDERS = frozenset({
    "ceo@bloomberg.example",
    "cfo@bloomberg.example",
    "board@bloomberg.example",
})

SENDER_WEIGHTS = {"vip": 50, "internal": 20, "external": 5}
URGENCY_WEIGHTS = {"low": 0, "normal": 10, "high": 25}
