# R2-16 · Portfolio P&L: interviewer notes

~360 lines. Finance methodology bugs where the **README is the spec**. No concurrency. The skill tested: turning a methodology paragraph
into a precise test, and finding the one line that deviates.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| PNL-1601 realized P&L | Lots are consumed FIFO, but realized P&L uses the **average cost** of all open lots | `services/lots.py::build_lots` | Rewriting the lot engine. The fix is computing P&L per lot slice inside the existing FIFO loop |
| PNL-1602 stale unrealized | `close_on_or_before` orders by `price_date` **ascending**, so it picks the **oldest** price | `repositories/market.py::PriceRepository` | Using `MAX(price_date)` without the `<= as_of` bound (leaks future prices) |
| PNL-1603 split | `apply_splits` adjusts lots with `opened >= effective` (after the split) instead of before | `services/lots.py::apply_splits` | Also adjusting post-split buys (double-adjusting). The ticket's example covers both sides |
| PNL-1604 book total | `book_total_usd` adds native-currency P&L across currencies | `services/pnl.py::book_total_usd` | Converting at trade-date rates (README: valuation-date rate) |

## Discussion prompts
- PNL-1601: "What does the tax report call this? Why would FIFO and average cost diverge only for multi-lot positions?" (A test with a
  single buy can't tell them apart. That's why the visible tests pass.)
- PNL-1603: ask the candidate to compute the ticket's 850 by hand **before** prompting the agent.

## Out-of-scope smells
- `build_lots`'s type hint says it returns 2 values; it returns 3. Cosmetic, but the agent may flag it. A good candidate notes it and moves on.
- Split handling relies on unique effective dates per security (`applied` set keyed by date).

## Strong prompts
- "Replay the PNL-1601 example through `build_lots` step by step: lots before, lots after, realized. Don't change code."
- "Which SQL decides which price is used for unrealized P&L? Show me what it returns for an as-of date with three candidate prices."
