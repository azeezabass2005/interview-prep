# R2-05 · Wallet Ledger: interviewer notes

~440 lines. The README lists explicit **ledger invariants**. The best candidates quote the invariant a ticket violates before touching code.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| PAY-501 overdraft | Check-then-act + absolute write: `withdraw` reads the balance, checks, then `set_balance(old - x)`. Two instances both pass the check; the second write overwrites the first | `services/wallets.py::withdraw`, `repositories/accounts.py::set_balance` | Process lock; "re-read before writing" |
| PAY-502 vanished transfer | `transfer` = `withdraw()` (own commit) then `deposit()` (own commit). If the deposit fails, the withdrawal stays | `services/wallets.py::transfer` | "Check the target is open first": still racy (it can close in between) and not atomic. Compensating "refund" logic is fragile |
| PAY-503 missing cent | `int(float(text) * 100)` truncates `434.99999…` | `services/money.py::parse_amount` | **AC proposes a display fix** (round in `format_cents`). The stored balance is already wrong; `format_cents` is integer-exact. Also breaks invariant 3 nowhere visible. Candidate should push back |
| PAY-504 statement gaps | Keyset pagination on `created_at` only; rows sharing the boundary timestamp are skipped | `repositories/entries.py::page_after`, `services/statements.py::page` | Switching to OFFSET pagination (unstable under inserts). Correct: a composite cursor `(created_at, entry_id)` |

## PAY-501 in depth
**Invariant:** balance ≥ 0 and balance == Σ entries, under any interleaving.

| Option | Verdict |
|---|---|
| Lock in `WalletService` | Reject: several instances |
| Re-read balance right before writing | Reject: window shrinks, doesn't close |
| `UPDATE accounts SET balance_cents = balance_cents - ? WHERE account_id = ? AND balance_cents >= ? AND status = 'OPEN'`, check rowcount, **and insert the entry in the same transaction** | **Accept** |
| `BEGIN IMMEDIATE` around read-check-write | Accept (SQLite-specific serialisation; mention `SELECT … FOR UPDATE` in Postgres) |

The entry insert must be in the **same transaction** as the balance change, or invariant 3 can still break on a crash.

**Deterministic test:** two `WalletService` instances, patch `AccountRepository.get` so the first two calls wait on `Barrier(2)` (both see
$100). One must succeed and one must get `InsufficientFunds`; final balance $20 == Σ entries.

## PAY-502
Single transaction: debit (conditional) + credit (conditional on target OPEN) + two entries; roll back if either update affects 0 rows.

## PAY-503
`Decimal(text)`, reject more than 2 dp (`"1.005"`), then `int(amount * 100)`. What to say about the AC: "format_cents is exact integer
arithmetic; the cent is lost at parse time. Rounding on display would hide a real accounting error."

## Out-of-scope smells
- `FraudMonitor.flags` lives in memory per instance (useless across instances). Mention, don't fix.
- `close_account` doesn't check for a zero balance.

## Strong prompts
- "For each README ledger invariant, show me the code path that is supposed to guarantee it. Don't change code."
- "In `withdraw`, which statements must happen atomically for invariants 2 and 3 to hold? Which layer can guarantee that across instances?"
