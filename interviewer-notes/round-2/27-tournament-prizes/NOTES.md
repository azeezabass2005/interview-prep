# R2-27 · Card Room Tournament Manager: Interviewer Guide

~300 lines in `tourney/`. One passing test (heads-up, with a bounty). The domain has a lot of moving parts (registration windows,
re-entries, tie places), so the candidate must build multi-step scenarios. Helpers to generate a 20-player field are a good sign.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Rake vs guarantee order | Rake comes out of the prize side first; the guarantee is a floor on the **pool**. No rake on the overlay. |
| "Up to 10 entries" | Inclusive: 10 entries pay 2 places. |
| Late reg "through level 6" | Entries allowed while the current level ≤ 6. |
| Max re-entries | 2 re-entries = 3 entries per player in total. |
| Tie straddling the last paid place | Share only the paid places covered (e.g. 2 players tied for 5th of 5 paid split the 5th prize). |
| Bounty on a re-entry | Each entry has its own $10 bounty; it's paid out on every elimination. |
| Players who never finish (no-shows) | Out of scope. |

## Code map
| Module | Responsibility |
|---|---|
| `services/registration.py` | Create, enter/re-enter, late-reg window, start, levels |
| `services/play.py` | Eliminations, bounty awards, finish |
| `services/pool.py` | Prize side, rake, guarantee, payout brackets, place amounts |
| `services/results.py` | Finishing places from final eliminations; prize allocation |
| `models.py`, `store.py`, `api.py`, `app.py` | Data, storage, facade, wiring |

## Planted bugs (5)

### B1 · Rake taken from the guarantee overlay
- **Where:** `pool.py::prize_pool`: `max(side, guarantee) - rake`.
- **Test:** 20 entries → pool 200,000 cents (buggy 191,000). 61 entries → 247,050 (unaffected: a good control).
- **Fix:** `max(side - rake, guarantee)`.
- **Hints:** "Turn the spec's 20-entry example into a test."

### B2 · 10 entries pay 3 places
- **Where:** `pool.py::percentages`: `entry_count < max_entries`.
- **Test:** 10-entry tournament → exactly 2 players receive prizes; 30 entries → 3.
- **Fix:** `<=`.
- **Hints:** "Test the bracket edges in the table."

### B3 · Tied players each get the best place's prize
- **Where:** `results.py::compute_prizes`: `covered[0]` for every tied player.
- **Test:** spec example: ben and cy tied for 2nd/3rd at 20 entries → 50,000 each; total prizes == pool.
- **Fix:** `split_evenly(sum(covered), players)` (it's already imported and correct).
- **Hints:** "Does the sum of prizes equal the pool when there's a tie?"

### B4 · Third re-entry accepted
- **Where:** `registration.py::enter`: `len(previous) > MAX_REENTRIES + 1` double-counts the original entry, so a 3rd re-entry (4th entry) is accepted.
- **Test:** enter, bust, re-enter, bust, re-enter, bust → a further entry is rejected (409).
- **Fix:** `len(previous) > MAX_REENTRIES` (previous entries include the original).
- **Hints:** "How many entries can one player buy in total?"

### B5 · Late registration closes one level early
- **Where:** `registration.py::registration_open`: `t.level < LATE_REG_LAST_LEVEL`.
- **Test:** at level 6 a new player can enter; at level 7 they can't.
- **Fix:** `<=`.
- **Hints:** "What does 'through the end of level 6' mean for level 6 itself?"

## Red herrings
- Leftover pool cents go to 1st (`place_amounts`): correct.
- Bounty splitting among several pot winners: correct.
- `final_eliminations` sorts hands descending: later hand = better place. Correct.

## Questions about the candidate's fixes (data structures)
- **B3/places:** "`final_eliminations` rebuilds a dict over every elimination at the end: O(E). If the director wants live standings after every hand, what would you maintain incrementally?" (A stack of elimination groups; places assigned as players bust: place = live players before the hand − group size + 1. O(1) per bust.)
- **B4:** "`entries_for(player)` scans all entries: O(n) per registration, O(n²) for a big field. Fix?" (A dict player → list of entries; or a counter + current live entry.)
- **Pool:** "Why integer cents and floor division rather than Decimal here?" (Exact, simpler; the leftover rule handles the rounding explicitly.)
- **General:** "`live_players()` builds a sorted set every call. Where is it called, and what does it cost?" (In every elimination: O(n log n). Keep a set of live players updated on bust/enter.)

## Feature requests
1. **"Progressive knockout (PKO): half of each bounty goes to the eliminator in cash, half is added to the eliminator's own bounty."** Strong answer: bounty becomes per-player state that grows; split rounding; what happens to the winner's own bounty (they keep it); tests that total bounty money is conserved.
2. **"Deal-making at the final table: the remaining players agree to split the remaining prize money by chip count (ICM-lite: chip-proportional)."** Strong answer: input chip counts; only unpaid places are redistributed; rounding and conservation; the director confirms.
3. **"Multi-day tournament: day 1 flights A and B merge into day 2."** Strong answer: entries across flights pooled; a player bagging chips in two flights keeps the bigger stack; re-entry limits per flight vs total (ask PM).

## Scoring signals
- **Strong:** builds a field-generator helper; checks `sum(prizes) == pool` as an invariant (finds B3); probes every boundary word ("up to", "through", "at most").
- **Weak:** only heads-up scenarios; misses registration rules entirely.
