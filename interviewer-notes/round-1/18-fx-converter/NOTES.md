# 18 · FX Payments Converter: interviewer notes

Code: `fx/`. Shape: quote-direction conventions (invert or not), tiers keyed on the right base (USD equivalent), rounding direction, per-currency precision, freshness check.

## PM answers

| Topic | Answer |
|---|---|
| Tier base | USD equivalent of the **source** amount at mid. |
| Tier boundaries | $10,000 exactly → 0.50% (as coded in `spread_for`). |
| Same currency | Out of scope (nice: reject or 1:1 with no spread). |
| Stale = | Older than 60 s: `now - at > 60 s`. Exactly 60 s is still fresh. |
| Unknown currency minor units | Should be an error, not a silent default of 2. |
| Inverting pairs | Yes: `USDJPY 151.20` means 1 JPY = 1/151.20 USD. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `rates.py::usd_per_unit` | USD-base pairs (`USDJPY`, `USDCHF`) aren't inverted | `return 1 / rate` | 1,512 JPY → USD = 9.90 |
| B2 | `convert.py::quote` | Spread tier chosen on the **source amount**, not its USD equivalent | `spread_for(amount * source_usd)` | 9,000 GBP → USD = 11,372.85 (0.5%) |
| B3 | `convert.py::quote` | `ROUND_HALF_UP`; the spec says always down | `ROUND_DOWN` | 100 EUR → USD = 107.41 |
| B4 | `currencies.py` | JPY missing, so it silently defaults to 2 decimals | add `"JPY": 0` (and ideally fail on unknown currencies) | `minor_units("JPY") == 0` |
| G1 | `rates.py::usd_per_unit` | Stale check missing (`MAX_AGE` and `StaleRate` defined, never used) | raise `StaleRate` if `now - at > MAX_AGE` | rate set 61 s ago → raises |

The spec's own example (EUR → JPY = ¥162,411) needs B1 and B4 fixed, and it's untested.

**Clue:** `MAX_AGE` and `StaleRate` are unused. The default in `minor_units` hides missing data. A candidate who says "I'd rather fail loudly here" is showing good judgement.

**Red herring:** `mid = source_usd / target_usd` is correct once `usd_per_unit` is correct. Agents often "fix" this line instead of the real bug in `rates.py`. That's a great moment to see whether the candidate verifies the agent's claim.

## Follow-ups
- Why Decimal for rates? What precision should the cross rate keep?
- The rate lookup scans all pairs (O(pairs)). Better: index by currency. Worth it? With ~30 pairs, no.
