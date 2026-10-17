# R1-30 · Capped Index: Interviewer Guide

One file, `capped.py` (~85 lines), with one passing test (two equal stocks). **The spec example fails on the
buggy code** (B1: one capping pass leaves B at 30%), the natural first test. This one is squarely in Bloomberg Index Services' domain.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly at the cap | Allowed (not "above"). |
| Proportional to what? | Current weights of uncapped stocks. |
| Residue recipient when all are capped | Any (alphabetical first). Out of scope. |
| A stock leaving the index | Its whole old weight counts in turnover. |
| Infeasible cap | Error (already handled). |

## Code map
`eligible` · `raw_weights` · `apply_cap` · `publish` · `turnover` · `IndexCalculator.rebalance`.

## Planted bugs (5)

### B1 · Capping is one pass
- **Where:** `apply_cap`.
- **Test:** the spec example → A/B/C 25.0000, D 16.6667, E 8.3333 (buggy B 30.0000).

### B2 · Rounding down, not half-up
- **Where:** `publish`: `ROUND_DOWN`.
- **Test:** sizes 1/1/1/3 → A **16.6667** (buggy 16.6666, with the residue dumped elsewhere).

### B3 · Float ignored
- **Where:** `raw_weights`.
- **Test:** equal size, float 1.0 vs 0.5 → **66.6667 / 33.3333**.

### B4 · Residue can go to a capped stock
- **Where:** `publish` ignores `cap` (parameter unused: clue).
- **Test:** cap 50%, A capped, three equal others → A stays **50.0000** (buggy 49.9999).

### B5 · Turnover ignores removed stocks
- **Where:** `turnover` iterates `new` only.
- **Test:** {A 50, B 50} → {A 50, C 50} → **50** (buggy 25).

Hints: (1) "the example is your first test"; (2) "which parameter of `publish` is never read?"

## Red herrings
- Eligibility uses `>=` everywhere: correct ("at least").
- The infeasible-cap guard: correct.

## Questions about the candidate's fixes (data structures)
- **B1:** "Your loop is O(k·n), k ≤ n rounds. Faster?" (Sort descending once and walk, deciding capped vs uncapped with a running remainder: O(n log n).) "Prove termination." (Each round caps at least one more stock.)
- **B4:** "Why must the residue avoid capped stocks?" (It could push them over the cap: the invariant.)
- **History list:** "Turnover only needs the previous weights. Keep 20 years of daily history?" (Store only diffs or keep the last one in memory and the rest on disk.)
- **Decimal precision:** "What precision context does Decimal use, and why does `excess * v / base` matter?" (28 digits by default; division error accumulates over rounds — negligible here.)

## Feature requests
1. **"Sector cap of 30% on top of the single-stock cap."** Strong answer: nested constraints iterated until both hold; tests where the sector cap binds.
2. **"Buffer rule: existing members stay eligible down to $400M."** Strong answer: eligibility depends on previous membership; pass the previous members in.
3. **"Index level continuity with a divisor."** Strong answer: new divisor so the level doesn't jump at the rebalance; store the level history.

## Scoring signals
- **Strong:** tests the example first; reasons about the cap invariant for the residue; constructs a removal for turnover.
- **Weak:** can't explain why the example fails after the first pass.
