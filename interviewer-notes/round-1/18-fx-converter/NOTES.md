# R1-18 · FX Converter: Interviewer Guide

One file, `fx.py` (~90 lines), with one passing test (book a fresh quote). **The spec example fails on the buggy code** (B2: spread
direction), so a candidate who tests the example finds the first bug quickly.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Booking at exactly 30 s | Allowed. |
| Limit day | UTC calendar day of the booking. |
| USD equivalent rate | Mid rate at quote time (stored on the quote). |
| Rate updated after quoting | The quote keeps its rate. |
| Rounding | Always down, to the target's minor unit. |

## Code map
`set_rate` · `mid` (direct and cross) · `quote` (spread, rounding, expiry) · `book` (status, expiry, daily limit).

## Planted bugs (5)

### B1 · Cross rate inverted
- **Where:** `mid`: `rates[source] / rates[target]`. Only non-USD pairs take this branch.
- **Test:** EUR → GBP mid = 0.80 ÷ 0.92 = **0.869565** (buggy 1.15).

### B2 · Spread in the client's favour
- **Where:** `quote`: `1 + SPREAD`.
- **Test:** the spec example → **EUR 915.40** (buggy 924.60).

### B3 · JPY gets two decimals
- **Where:** `quote`: fixed `0.01`; `MINOR_UNITS` used only for validation (clue).
- **Test:** USD 100 → **JPY 15422** (buggy 15422.50).

### B4 · Expires one tick early
- **Where:** `book`: `now >= expires_at`.
- **Test:** booking at exactly +30 s succeeds.

### B5 · Daily limit counts source units, not USD
- **Where:** `book`: `usd = quote["amount"]`; `usd_mid` is stored but never read (clue).
- **Test:** JPY 1,000,000 (≈ USD 6,450) → allowed (buggy: refused as 1,000,000 > 50,000).

Hints: (1) "what does the client get if the spread is in their favour?"; (2) "which stored fields are never read?"

## Red herrings
- A quote can't be booked twice: correct.
- `USD` can't be set: correct (it's the base).

## Questions about the candidate's fixes (data structures)
- **Daily limit:** "`book` scans all bookings ever: O(B). Better?" (Dict (client, day) → used USD; O(1). Old days can be evicted.)
- **Quotes dict grows forever.** "What would you do?" (Expire: heap of (expires_at, id) to purge, or TTL cache.)
- **B3:** "Why `Decimal(1).scaleb(-n)` / `Decimal('1e-0')`?" (Builds the quantum for n decimals.) "Where would you keep currency metadata?" (Currency table: minor units, rounding, symbol.)
- **Float vs Decimal for rates:** "1/0.92 isn't exact even in Decimal. Implications?" (Precision context; round only at the end; store rates with enough digits.)

## Feature requests
1. **"Two-way quotes: show both the buy and sell rate."** Strong answer: bid/ask from mid ± spread; the client picks a side.
2. **"Spread by client tier and currency pair."** Strong answer: a lookup table (tier, pair) → spread with defaults.
3. **"Forward contracts: book now, settle in 30 days."** Strong answer: forward points; the value date; limits counted on booking day or value day? (Ask PM.)

## Scoring signals
- **Strong:** starts with the example (B2); tests a cross pair and JPY; spots unused `usd_mid`.
- **Weak:** only USD → EUR.
