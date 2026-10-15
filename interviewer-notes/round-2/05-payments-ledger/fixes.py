FIXES = [
    ("ledger/services/money.py", "from ..errors import InvalidAmount",
     "from decimal import Decimal, InvalidOperation\n\nfrom ..errors import InvalidAmount"),
    ("ledger/services/money.py",
     "    try:\n        cents = int(float(text) * 100)\n    except (TypeError, ValueError):",
     "    try:\n        amount = Decimal(str(text))\n    except (InvalidOperation, TypeError, ValueError):\n"
     "        raise InvalidAmount(f\"not an amount: {text!r}\")\n"
     "    if not amount.is_finite() or amount.as_tuple().exponent < -2:\n"
     "        raise InvalidAmount(\"at most 2 decimal places\")\n"
     "    try:\n        cents = int(amount * 100)\n    except (TypeError, ValueError):"),
    ("ledger/repositories/accounts.py", "from typing import Optional",
     "from datetime import datetime\nfrom typing import List, Optional, Tuple"),
    ("ledger/repositories/accounts.py",
     "    def set_status(self, account_id: str, status: str) -> None:",
     """    def apply_movements(self, legs: List[Tuple[str, int, str]], reference: str, at: datetime) -> bool:
        \"\"\"Apply (account_id, signed cents, kind) legs atomically. False if any leg is not allowed.\"\"\"
        with self._db.transaction() as conn:
            conn.execute("BEGIN IMMEDIATE")
            for account_id, cents, kind in legs:
                cur = conn.execute(
                    "UPDATE accounts SET balance_cents = balance_cents + ? "
                    "WHERE account_id = ? AND status = 'OPEN' AND balance_cents + ? >= 0",
                    (cents, account_id, cents))
                if cur.rowcount != 1:
                    conn.rollback()
                    return False
                conn.execute(
                    "INSERT INTO entries (account_id, amount_cents, kind, reference, created_at) VALUES (?, ?, ?, ?, ?)",
                    (account_id, cents, kind, reference, at.isoformat()))
        return True

    def set_status(self, account_id: str, status: str) -> None:"""),
    ("ledger/services/wallets.py",
     """        cents = parse_amount(amount)
        account = self._open_account(account_id)
        self._accounts.set_balance(account_id, account.balance_cents + cents)
        self._entries.insert(account_id, cents, "DEPOSIT", reference, self._clock.now())
        return self.get(account_id)""",
     """        cents = parse_amount(amount)
        self._open_account(account_id)
        self._move([(account_id, cents, "DEPOSIT")], reference)
        return self.get(account_id)

    def _move(self, legs, reference: str) -> None:
        if not self._accounts.apply_movements(legs, reference, self._clock.now()):
            for account_id, cents, _ in legs:
                self._open_account(account_id)
            raise InsufficientFunds("insufficient funds")"""),
    ("ledger/services/wallets.py",
     """        cents = parse_amount(amount)
        account = self._open_account(account_id)
        if account.balance_cents < cents:
            raise InsufficientFunds(f"balance {account.balance_cents} < {cents}")
        self._accounts.set_balance(account_id, account.balance_cents - cents)
        self._entries.insert(account_id, -cents, "WITHDRAWAL", reference, self._clock.now())""",
     """        cents = parse_amount(amount)
        self._open_account(account_id)
        self._move([(account_id, -cents, "WITHDRAWAL")], reference)"""),
    ("ledger/services/wallets.py",
     "        self.withdraw(source, amount, reference)\n        self.deposit(target, amount, reference)",
     "        cents = parse_amount(amount)\n"
     "        self._move([(source, -cents, \"TRANSFER_OUT\"), (target, cents, \"TRANSFER_IN\")], reference)"),
    ("ledger/repositories/entries.py",
     """            if after is None:
                rows = conn.execute(
                    "SELECT * FROM entries WHERE account_id = ? ORDER BY created_at LIMIT ?", (account_id, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM entries WHERE account_id = ? AND created_at > ? ORDER BY created_at LIMIT ?",
                    (account_id, after, limit),
                ).fetchall()""",
     """            if after is None:
                rows = conn.execute(
                    "SELECT * FROM entries WHERE account_id = ? ORDER BY created_at, entry_id LIMIT ?",
                    (account_id, limit)).fetchall()
            else:
                after_ts, after_id = after.rsplit("|", 1)
                rows = conn.execute(
                    "SELECT * FROM entries WHERE account_id = ? AND "
                    "(created_at > ? OR (created_at = ? AND entry_id > ?)) ORDER BY created_at, entry_id LIMIT ?",
                    (account_id, after_ts, after_ts, int(after_id), limit)).fetchall()"""),
    ("ledger/services/statements.py",
     "next_cursor = entries[-1].created_at.isoformat() if len(entries) == limit else None",
     "next_cursor = f\"{entries[-1].created_at.isoformat()}|{entries[-1].entry_id}\" if len(entries) == limit else None"),
]
