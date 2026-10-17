# R1-24 · Crowdfunding: Interviewer Guide

One file, `crowd.py` (~110 lines), with one passing test (pledges add up). The spec example passes on the buggy code (every charge
succeeds; the total is above the goal).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Pledge at exactly the deadline | Rejected. |
| Total exactly equal to the goal | Funded. |
| Funded on pledges, but charges fail and collected < goal | Still funded; the creator gets what was collected. |
| Change tier to a full tier | Rejected; the old pledge stays. |
| How many retries? | One retry (two attempts in total). |

## Code map
`create` · `_open` (deadline) · `_claim` (tier rules) · `pledge` · `change` · `cancel` · `total` · `settle` (charges, retries, fees).

## Planted bugs (5)

### B1 · Tier slots never freed
- **Where:** `cancel` and `change`.
- **Test:** 1-slot tier; ana takes it and cancels; ben takes it → taken = **1** (buggy: ben refused).

### B2 · Goal exactly met isn't funded
- **Where:** `settle`: `<= c.goal`.
- **Test:** goal $1,000, pledged $1,000 → funded.

### B3 · Pledges accepted at the deadline
- **Where:** `_open`: `at > deadline`.
- **Test:** pledge at exactly the deadline → error.

### B4 · Fixed fee charged for failed pledges
- **Where:** `settle`: `PROCESSING_FIXED * len(c.pledges)`.
- **Test:** one success ($100), one double decline → processing **$3.20** (buggy $3.40).

### B5 · No retry
- **Where:** `settle`.
- **Test:** decline then success → collected $100, no failures.

Hints: (1) "what happens to `taken` when a pledge goes away?"; (2) "write a fake gateway that declines".

## Red herrings
- Settlement only after the deadline: correct.
- Platform fee on collected (not pledged): correct.

## Questions about the candidate's fixes (data structures)
- **B1:** "`taken` is a counter that must mirror the pledges. Alternative?" (Derive it: count pledges with that tier — O(P) but never drifts; or keep a set of backers per tier.) Discuss trade-offs.
- **Pledges dict keyed by backer:** "Why does that enforce 'one pledge per backer'?" (Key uniqueness.) "Pledge history?" (Append-only list of changes for audit.)
- **Retries:** "Your retry is inline. In production?" (A queue with backoff; idempotency keys so a retry never double-charges.)
- **Settlement of 100,000 pledges:** "What would you change?" (Batch, resume after crash — per-pledge charge status persisted.)

## Feature requests
1. **"Stretch goals: unlock bonus rewards at 150% and 200%."** Strong answer: thresholds evaluated at settlement; announced live; tests at exact thresholds.
2. **"Add-ons: buy extra items with a pledge."** Strong answer: line items; inventory per add-on; total pledge = base + add-ons.
3. **"Refund window after settlement."** Strong answer: refunds reduce payout before it's sent; fee policy on refunds.

## Scoring signals
- **Strong:** writes a scripted gateway double; tests the deadline and goal boundaries; checks tier counts after cancel.
- **Weak:** only the happy path.
