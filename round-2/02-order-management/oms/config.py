MAX_ORDER_QTY = 1_000_000
# (price threshold, tick): prices >= threshold use the tick. Checked from the top down.
TICK_TABLE = [
    (1.00, 0.01),
    (0.00, 0.0001),
]
SIDES = ("BUY", "SELL")
