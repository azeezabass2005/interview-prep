FIXES = [
    ("ledger.py", "        if self.balance(sender) < amount + fee:", "        if self.available(sender) < amount + fee:"),
    ("ledger.py", "        amount = Decimal(str(amount))\n        if amount <= 0 or sender in SYSTEM",
     "        if key in self.by_key:\n            return self.transfers[self.by_key[key]]\n        amount = Decimal(str(amount))\n        if amount <= 0 or sender in SYSTEM"),
    ("ledger.py", "        if amount < FEE_THRESHOLD:", "        if amount <= FEE_THRESHOLD:"),
    ("ledger.py", "        return (amount * FEE_RATE).quantize(CENT, rounding=ROUND_HALF_UP)",
     "        return max((amount * FEE_RATE).quantize(CENT, rounding=ROUND_HALF_UP), MIN_FEE)"),
    ("ledger.py", "        self._post(f\"rev-{transfer_id}\", (t.receiver, -t.amount), (t.sender, t.amount))",
     "        self._post(f\"rev-{transfer_id}\", (t.receiver, -t.amount), (\"FEES\", -t.fee), (t.sender, t.amount + t.fee))"),
    ("ledger.py", "        h = self.holds.pop(hold_id)\n        return self.transfer(key, h[\"account\"], receiver, h[\"amount\"])",
     "        h = self.holds.pop(hold_id)\n        try:\n            return self.transfer(key, h[\"account\"], receiver, h[\"amount\"])\n        except LedgerError:\n            self.holds[hold_id] = h\n            raise"),
]
