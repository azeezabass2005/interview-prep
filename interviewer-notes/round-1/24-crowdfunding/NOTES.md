# 24 · All-or-Nothing Crowdfunding: interviewer notes

Code: `crowd/campaign.py`. Shape: lifecycle (open → closed), limited inventory with release on cancel, threshold (≥), conditional fees, fee base order.

## PM answers

| Topic | Answer |
|---|---|
| Deadline boundary | Pledges must be strictly before the deadline. |
| Pledge more than tier min | Allowed (the whole amount counts). |
| One backer, many pledges | Allowed. Each pledge is charged separately and pays its own $0.20. |
| Processing base | 3% of the **total**, not total minus platform fee. |
| Failed campaign | Fees are 0 and nobody is charged. |
| Cancel after the deadline | Not allowed (nice to guard). |
| Stretch goals | Out of scope. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `pledge` | `claimed > limit` allows limit + 1 | `>=` | limit 2: the third DELUXE pledge is rejected |
| B2 | `total` | Cancelled pledges still counted | sum active only | 900 + 200 (cancelled) → not funded |
| B3 | `close` | `total > goal`: exactly at goal fails | `>=` | pledges total exactly 1,000 → funded |
| B4 | `close` | Fees reported on unfunded campaigns | zero fees unless funded | not funded → fees 0.00 |
| B5 | `close` | Processing fee is 3% of (total − platform fee) | 3% of total | spec example payout 1,099.00 (buggy 1,100.80) |
| G1 | `pledge` | The deadline is never checked (`_clock` unused) | reject when `now >= deadline` | pledge after the deadline → rejected |

**Visible-test trap:** `test_not_funded` only checks payout and charged, and passes despite B4. Good candidates extend it with the fee assertions.

**Red herring:** `cancel` mutating `cancelled` (rather than deleting) is fine and keeps history.

## Follow-ups
- Where would you enforce the tier limit if pledges came in concurrently? (Round 2 territory: a DB constraint or a conditional update.)
- Why return `charged` from close? (The payment step needs an explicit list; it also proves nobody is charged on failure.)
