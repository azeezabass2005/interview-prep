FIXES = [
    ("potluck/codes.py", "        return str(value)", "        return f\"{value:0{CODE_LENGTH}d}\""),
    ("potluck/matching.py", "    common = Counter(entry_code) & Counter(winning_code)\n    return sum(common.values())",
     "    return sum(1 for a, b in zip(entry_code, winning_code) if a == b)"),
    ("potluck/services/payouts.py", "    for tier in sorted(TIER_SHARES):", "    for tier in sorted(TIER_SHARES, reverse=True):"),
    ("potluck/services/draws.py", "        entries = self._store.entries_for_draw(draw.draw_id)\n",
     "        entries = self._store.entries_for_draw(draw.draw_id, active_only=True)\n"),
    ("potluck/services/entries.py",
     "    def active_count(self, participant_id: str) -> int:\n        return sum(1 for e in self._store.entries_for_participant(participant_id) if e.status == ACTIVE)",
     "    def active_count(self, participant_id: str, draw_id: int) -> int:\n"
     "        return sum(1 for e in self._store.entries_for_participant(participant_id)\n"
     "                   if e.status == ACTIVE and e.draw_id == draw_id)"),
    ("potluck/services/entries.py", "        if self.active_count(participant_id) + quantity",
     "        if self.active_count(participant_id, draw.draw_id) + quantity"),
]
