# R1-35 · Payments Ledger: Interviewer Guide

The Round 1 version of Round 2 #05. One file, `ledger.py` (~95 lines), with one passing test (a small transfer). **The spec example fails on the
buggy code** once the candidate checks balances: the $1,200 transfer exposes B4 (fee $0.60 instead of $1.00).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly $1,000 | No fee ("above"). |
| Fee on capture of a hold | Same rules as any transfer. |
| Same key, different amount | Return the original; move nothing. |
| Reverse when the receiver has spent the money | Allowed to go negative? No: out of scope; assume funds exist. |
| Reversal of a reversal | Not allowed. |

## Code map
`balance` / `available` · `_post` (zero-sum invariant) · `deposit` · `fee_for` · `transfer` · `reverse` · `hold` / `release` / `capture`.

## Planted bugs (5)

### B1 · Funds check ignores holds
- **Where:** `transfer` uses `balance`.
- **Test:** $100, hold $80, send $50 → **refused**.

### B2 · Idempotency key never checked
- **Where:** `transfer` writes `by_key` but never reads it (clue).
- **Test:** `k1` twice → Ana **$1,900**.

### B3 · Fee at exactly $1,000
- **Where:** `fee_for`: `amount < threshold` returns no fee only below; 1,000 is charged.
- **Test:** `fee_for(1000)` → **0.00**.

### B4 · No minimum fee
- **Where:** `fee_for`; `MIN_FEE` unused.
- **Test:** `fee_for(1200)` → **1.00**.

### B5 · Reversal keeps the fee
- **Where:** `reverse`.
- **Test:** send $1,500 then reverse → Ana back to **$2,000**, FEES **0**.

(The reference fix also restores a hold if its capture fails — a bonus issue some candidates notice: `capture` pops the hold before
the transfer can fail.)

Hints: (1) "write the invariant 'all balances sum to zero' as a test"; (2) "what is `by_key` for?"

## Red herrings
- `_post` rejects unbalanced entries: correct (and a useful invariant).
- Currency check: correct.

## Questions about the candidate's fixes (data structures)
- **Balances derived by scanning entries:** O(E) per balance. "Trade-offs vs a stored balance?" (Stored balance: O(1) but must be updated atomically with entries; derived: always correct, slow → snapshot + entries since snapshot.)
- **B2:** "Idempotency across servers?" (Unique constraint on the key in the DB, inserted in the same transaction as the entries.)
- **Holds dict:** "Expire holds after 7 days?" (Store expiry; heap by expiry for a sweeper.)
- **Decimal for money:** "Why not integer cents?" (Both fine; integers are faster and exact; Decimal is explicit about scale.)

## Feature requests
1. **"Multi-currency transfers with FX."** Strong answer: four legs (sender currency, FX account in each currency, receiver); rate snapshot; zero-sum per currency.
2. **"Partial reversal (refund part of a payment)."** Strong answer: track reversed amount; fee refund pro rata or not (ask); multiple partial reversals up to the amount.
3. **"Daily statement per account."** Strong answer: entries filtered by day; opening/closing balance; index entries by (account, day).

## Scoring signals
- **Strong:** writes the zero-sum invariant; tests idempotency; tests boundaries of the fee rule.
- **Weak:** only checks one balance after one transfer.
