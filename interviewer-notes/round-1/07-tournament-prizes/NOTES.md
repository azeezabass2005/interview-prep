# 07 · Tournament Prize Pool: interviewer notes

Code: `prizes/`. Shape: guarantee overlay (order of rake vs guarantee), bracket boundaries, tie splitting with competition ranking, cent conservation.

## PM answers

| Topic | Answer |
|---|---|
| Rake vs guarantee order | Rake comes out of the fees first. The guarantee is a floor on the **prize pool** (the house pays the overlay; there is no rake on the overlay). |
| "Up to 10" | Inclusive: exactly 10 entries pays 2 places; 30 pays 3. |
| Bracket based on entries or unique players? | Entries (re-entries included). |
| Tie straddling the last paid place | e.g. 3 tied for 5th with 5 places paid: they share the 5th place money three ways. |
| Players in standings who are not in entries | Invalid input; out of scope. |
| Leftover cents | 1st place gets the place-rounding leftover; tie-split leftovers go alphabetically within the tie. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `pool.py::prize_pool` | `max(fees, guarantee) - rake`: rake is taken from the overlay | `max(fees - rake, guarantee)` | 20 entries → 200,000 (buggy: 189,000) |
| B2 | `pool.py::payout_percentages` | `entry_count < max_entries` excludes the boundary | `<=` | 10 entries → 2 places |
| B3 | `payouts.py::compute_payouts` | Each tied player gets the full prize of the tie's first place | sum the places covered, split evenly | Tie for 2nd at 20 entries: 500.00 each |
| B4 | `payouts.py::compute_payouts` | `place += 1` (dense rank) instead of `+= len(group)` | `place += len(group)` | the finisher after the 2-way tie is 4th: unpaid with 3 places |
| B5 | `payouts.py::place_amounts` | Floors each place and drops the leftover cents | add `pool - sum(amounts)` to 1st | 61 entries: payouts sum to 301,950; 1st gets 120,781 |

**Red herring:** the visible test `test_re_entries_count` is a weak test. It barely asserts anything. A good candidate calls that out ("this test would pass even if re-entries were ignored").

## Follow-ups
- Why are standings a list of lists, not a dict of player → position? (The tie structure is explicit; a dict needs a positional convention.)
- How do you guarantee "sum == pool" structurally? (Compute the last share as the remainder, or assert in code.)
- What happens if the standings list fewer players than paid places? (Unpaid places: should money roll to the house? Ask.)
