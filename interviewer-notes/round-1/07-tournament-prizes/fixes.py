FIXES = [
    ("prizes/pool.py", "return max(entry_fees(entry_count), GUARANTEE_CENTS) - rake(entry_count)",
     "return max(entry_fees(entry_count) - rake(entry_count), GUARANTEE_CENTS)"),
    ("prizes/pool.py", "if max_entries is None or entry_count < max_entries:", "if max_entries is None or entry_count <= max_entries:"),
    ("prizes/payouts.py", "    return [pool * pct // 100 for pct in payout_percentages(entry_count)]",
     "    amounts = [pool * pct // 100 for pct in payout_percentages(entry_count)]\n"
     "    amounts[0] += pool - sum(amounts)\n"
     "    return amounts"),
    ("prizes/payouts.py",
     "        for player in sorted(group):\n            payouts[player] = amounts[place]\n        place += 1\n",
     "        names = sorted(group)\n"
     "        combined = sum(amounts[place:place + len(names)])\n"
     "        base, leftover = divmod(combined, len(names))\n"
     "        for i, player in enumerate(names):\n"
     "            payouts[player] = base + (1 if i < leftover else 0)\n"
     "        place += len(names)\n"),
]
