# R2-07 · Short Links: interviewer notes

~360 lines. The README's one-line invariant, "a code or alias, once assigned, must never point anywhere else", is the yardstick for
two of the four tickets.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| LNK-701 alias hijacked | Create checks `get(code)` (case-**sensitive** `=`), stores the alias as typed; visitor `lookup` is case-**insensitive** and returns the **newest** match | `services/links.py::create`, `repositories/links.py::lookup` | Fixing only `lookup` to return the oldest: hides the symptom, but duplicates still get created. The invariant needs normalisation at write time (+ uniqueness) |
| LNK-702 click counts | `ClickRecorder.record` does `set_clicks(link.clicks + 1)` with the value read at lookup: a lost update across instances | `services/analytics.py`, `repositories/links.py::set_clicks` | Recounting from `click_events` on read (a valid alternative, but a different design; ask about cost). Locks: no |
| LNK-703 expired redirects | `resolve` never checks `is_expired`; only `info` does | `services/links.py::resolve` | Putting the check in the API layer only (other callers of `resolve` would still redirect) |
| LNK-704 link overwritten | `LinkRepository.save` uses **`INSERT OR REPLACE`**, so a colliding generated code silently replaces the old row | `repositories/links.py::save` | **AC prescribes longer codes.** That lowers the probability but never makes it zero, and the replace is still there. The real fix: plain `INSERT` + retry with a new code on conflict |

## LNK-702 in depth
| Option | Verdict |
|---|---|
| `UPDATE links SET clicks = clicks + 1 WHERE code = ?` | **Accept** (store-owned, one statement) |
| Derive `clicks` from `COUNT(*) FROM click_events` | Accept with discussion (always consistent; costs a count per info request; could be cached) |
| Lock in `ClickRecorder` | Reject: multiple redirect instances |

**Deterministic test:** two `LinkService` instances; patch `LinkRepository.lookup` so the first two calls wait on `Barrier(2)`. Both read
`clicks = 0`. Assert `clicks == 2`.

## LNK-704 in depth
Test by **forcing the collision**: patch `generate_code` to return the same code twice. With only longer codes, that test still overwrites.
Also: event inserts and counter updates are separate transactions (fine for this ticket).

## Out-of-scope smells
- `abuse.is_blocked` is checked only at creation; a domain blocked later still redirects.
- `lookup` returns the newest match. Once 701 is fixed, at most one match exists.

## Strong prompts
- "Where is the case-insensitivity rule enforced on write, and where on read? Show me both. Don't change code."
- "Show me every SQL statement that can change an existing link's `target_url`."
