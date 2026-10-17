FIXES = [
    ("tournament.py", "        if self.entries.count(player) > 1 + MAX_REENTRIES:", "        if self.entries.count(player) >= 1 + MAX_REENTRIES:"),
    ("tournament.py", "TO_POOL * len(self.players)", "TO_POOL * len(self.entries)"),
    ("tournament.py", "            if count > minimum:", "            if count >= minimum:"),
    ("tournament.py", "            amounts[-1] += pool - sum(amounts)", "            amounts[0] += pool - sum(amounts)"),
    ("tournament.py", "sorted(chips, key=lambda p: chips[p], reverse=True)", "sorted(chips, key=lambda p: chips[p])"),
]
