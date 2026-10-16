# R1-24 · All-or-Nothing Crowdfunding: Interviewer Guide

~250 lines in `crowd/`. One passing test (an unfunded campaign charges nobody). Bugs: tier inventory (two different paths), lifecycle
state ignored at settlement, a threshold boundary, and fee accounting with failed charges.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Goal reached exactly | Funded ("at least"). |
| Funded test uses pledged or collected? | Pledged (active pledges at the deadline). Failures don't un-fund it. |
| Per-charge fee for failed charges | No: only successful charges. |
| Changing to the same tier | Allowed even if it's full (you already hold a slot). |
| Pledge exactly at the deadline | Rejected (must be before). |
| Stretch goal base | Active pledges at the deadline (same as the funding test). |

## Code map
| Module | Responsibility |
|---|---|
| `services/campaigns.py` | Create campaigns and tiers |
| `services/pledges.py` | Pledge, change, cancel; tier limits |
| `services/settlement.py` | Funding decision, charging, fees, stretch goal |
| `payments.py` | Fake card processor (configurable failures) |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Tier limit allows one extra
- **Where:** `pledges.py::pledge`: `claimed > limit`.
- **Test:** DELUXE limit 2 → the third DELUXE pledge is rejected (409).

### B2 · Cancelled pledges are charged
- **Where:** `settlement.py::settle`: `pledges = list(c.pledges.values())`.
- **Test:** pledges 900 + 200 (cancelled), goal 1,000 → not funded; and in a funded campaign the cancelled backer is never charged.
- **Fix:** active pledges only.

### B3 · Exactly at goal isn't funded
- **Where:** `settlement.py::settle`: `total > c.goal`.
- **Test:** one $1,000 pledge on a $1,000 goal → funded.

### B4 · Per-charge fee includes failed charges
- **Where:** `settlement.py::settle`: `PER_CHARGE_FEE × attempted`.
- **Test:** the spec example with one STANDARD charge failing → collected 1,165.00; processing 34.95 + 24 × 0.20 = 39.75 → payout **1,067.00**.

### B5 · Changing into a sold-out tier
- **Where:** `pledges.py::change`: validates the minimum but not the target tier's limit.
- **Test:** DELUXE limit 1 taken by ann; bob changes his STANDARD pledge to DELUXE → 409.

Hints: (1) the spec sentence; (2) "is the same rule enforced on every path that can violate it?" (B1/B5).

## Red herrings
- Pledge/cancel/change rejected after the deadline: correct.
- Fees rounded half-up: correct.

## Questions about the candidate's fixes (data structures)
- **B1/B5:** "`claimed` scans all pledges per check: O(P). How would you make tier counting O(1)?" (A counter per tier updated on pledge/change/cancel. Every mutation path must update it, which is exactly the B5 lesson.)
- **Concurrency:** "Two backers grab the last DELUXE slot at once on two servers. What breaks, and where would you enforce the limit?" (A conditional update / DB constraint on the tier count.)
- **Settlement:** "Charging is sequential. 50,000 backers? Partial failure mid-way? Idempotency?" (Batch + retries; a charge id per pledge so a re-run doesn't double-charge.)

## Feature requests
1. **"Add-ons: backers can add a $20 sticker pack to any tier pledge (limited to 200 packs)."** Strong answer: add-on inventory separate from tiers; change/cancel must release add-ons; amount = tier + add-ons.
2. **"Retry failed charges for 7 days after the deadline; payout only after retries finish."** Strong answer: charge state machine (PENDING → CHARGED/FAILED → RETRYING); the fee computation moves to final settlement.
3. **"Late pledges ('slacker backers') after a successful campaign, charged immediately."** Strong answer: a different flow (no all-or-nothing); fees per pledge; tier limits still enforced.

## Scoring signals
- **Strong:** looks for every code path that touches tier capacity; uses the fake payments to inject failures.
- **Weak:** never cancels or changes a pledge.
