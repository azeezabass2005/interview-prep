FIXES = [
    ("auction/pricing.py", "if current is None or bid.amount_cents > current.amount_cents:",
     "if current is None or bid.seq > current.seq:"),
    ("auction/pricing.py", "return sorted(bids, key=lambda b: (b.amount_cents, b.seq), reverse=True)",
     "return sorted(bids, key=lambda b: (-b.amount_cents, b.seq))"),
    ("auction/pricing.py",
     "    hammer = runner_up + INCREMENT_CENTS\n    return Result(lot.lot_id, winner.bidder, hammer, invoice_for(winner.amount_cents))",
     "    floor = lot.reserve_cents if lot.reserve_cents is not None else OPENING_PRICE_CENTS\n"
     "    hammer = max(min(runner_up + INCREMENT_CENTS, winner.amount_cents), floor)\n"
     "    return Result(lot.lot_id, winner.bidder, hammer, invoice_for(hammer))"),
    ("auction/house.py", "        if amount_cents <= 0:\n",
     "        if lot.closed:\n            raise AuctionError(\"lot is closed\")\n        if amount_cents <= 0:\n"),
]
