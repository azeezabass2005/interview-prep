# BLT-410: The blotter takes 9 seconds to load for busy desks

**Type:** Bug (performance) · **Priority:** Medium · **Reporter:** DBA team

## Description
The FX desk's blotter page takes about 9 seconds by mid-afternoon (around 3,000 trades) and the database is busy the whole time.
The DBA team sees thousands of identical small queries per page load, all for `SELECT * FROM counterparties WHERE id = ?`.

## Acceptance criteria
- Loading the blotter uses a fixed number of queries, however many trades or counterparties there are.
- The response stays exactly the same (same trades, same order, same counterparty names).

## Out of scope
- Pagination of the blotter (UX are designing it).
