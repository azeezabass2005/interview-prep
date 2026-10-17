FIXES = [
    ("auction/services/pricing.py", "    return sorted(best.values(), key=lambda b: (b.maximum, b.seq), reverse=True)",
     "    return sorted(best.values(), key=lambda b: (-b.maximum, b.seq))"),
    ("auction/services/pricing.py", "runner_up + increment_for(winner.maximum)", "runner_up + increment_for(runner_up)"),
    ("auction/services/bidding.py", "            lot.closes_at = lot.closes_at + timedelta(seconds=SOFT_CLOSE_SECONDS)",
     "            lot.closes_at = now + timedelta(seconds=SOFT_CLOSE_SECONDS)"),
    ("auction/services/invoices.py",
     "        winning_bid = leading_bids(store.bids_for(lot.lot_id))[0]\n        premium = (winning_bid.maximum * PREMIUM_RATE)",
     "        premium = (lot.hammer * PREMIUM_RATE)"),
    ("auction/services/invoices.py", "        deductible = lot.hammer - lot.fmv", "        deductible = max(lot.hammer - lot.fmv, Decimal(\"0\"))"),
]
