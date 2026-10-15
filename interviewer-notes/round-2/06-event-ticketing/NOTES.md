# R2-06 · Box Office: interviewer notes

~485 lines. Seat inventory is the classic "claim a scarce resource" problem. Watch for candidates who reason from the README policy rather than
the ticket text.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| TIX-601 hold race | `SeatService.hold` reads every seat, checks availability in Python, then writes holds unconditionally. Two instances both see AVAILABLE; the last write wins | `services/seating.py::hold`, `repositories/seats.py::set_hold` | Fixing only `purchase` (it's already correct; the lie happens at hold time). All-or-nothing across several seats needs **one transaction** |
| TIX-602 holds stuck | `is_available` compares `hold_expires_at` (ISO with `T`) against `str(now)` (space separator). On the same date `'T' > ' '`, so a hold never looks expired until the date changes | `services/seating.py::is_available` | Changing the hold duration. The fix is comparing datetimes (or `now.isoformat()` consistently). `purchase` already does it right; the inconsistency is the clue |
| TIX-603 refund denied | `hours_until_event` subtracts **UTC now** from the **venue-local** start time. For New York that's 4 h off, so 50 h looks like 46 h | `services/refunds.py::hours_until_event` | **AC contradicts the policy** (asks to change 48 h → 24 h). That would also refund people inside the real 48 h window. Root cause is time zones; the policy stays |
| TIX-604 fee per order | `order_amounts` charges `SERVICE_FEE_CENTS` once | `services/pricing.py` | Straightforward; good for checking tests with N > 1 |

## TIX-601 in depth
**Invariant:** a seat is held by at most one unexpired customer, and sold at most once.

| Option | Verdict |
|---|---|
| Re-check availability right before `set_hold` | Reject: still racy |
| Lock in `SeatService` | Reject: multiple instances |
| Conditional update per seat (`… WHERE status='AVAILABLE' OR (status='HELD' AND hold_expires_at < :now)`) in **one transaction** (`BEGIN IMMEDIATE`), roll back if any seat's rowcount is 0 | **Accept** |
| Separate `seat_holds` table with a PK on (event, seat) + cleanup of expired rows | Accept; more moving parts |

**Deterministic test:** two `SeatService` instances; patch `SeatRepository.get` so the first two calls wait on `Barrier(2)`. Exactly one
hold succeeds.

## TIX-603 in depth
Fix: `starts_at_local.replace(tzinfo=ZoneInfo(venue_tz)).astimezone(timezone.utc)` vs aware UTC now (or make now naive UTC consistently).
Test both sides of the boundary: 50 h before → refund; 44 h before → denied. If the candidate changed the window to 24 h, the 44 h case
exposes it.

## Out-of-scope smells
- `CheckoutService.purchase` inserts the order and marks seats SOLD in **separate** transactions (a crash in between = paid order, unsold seats).
  Great to call out as a remaining risk.
- Refund doesn't verify the requester owns the order.

## Strong prompts
- "Compare how `SeatService.is_available` and `CheckoutService.purchase` decide whether a hold is expired. Are they consistent? Don't change code."
- "The ticket asks to move the refund window to 24 h. Using README.md, is that consistent with policy? What else explains a 50 h request being denied?"
