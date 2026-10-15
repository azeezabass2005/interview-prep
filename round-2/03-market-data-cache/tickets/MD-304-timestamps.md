# MD-304: `updated_at` is off by several hours for our London users

**Type:** Bug · **Reporter:** Client portal team · **Priority:** Low

## Description
The `updated_at` field looks like UTC (it ends with `Z`) but is several hours off depending on which data center served the request.
New York servers are 4–5 hours behind, Tokyo ones 9 hours ahead.

## Acceptance criteria
- `updated_at` is the quote time in UTC with a `Z` suffix, no matter where the server runs.

## Out of scope
- Displaying local time in the portal UI.
