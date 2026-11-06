# RES-104: The report list sometimes shows another firm's research

**Type:** Bug · **Priority:** High · **Reporter:** Client Services

## Description
Two clients, on calls a minute apart, saw different lists from what their firms subscribe to. A Rates-only client saw an empty
list on the "All sectors" view even though Rates research was published this morning; an Energy-only client on another call saw
nothing but Rates. Refreshing a minute later fixed it for both. Opening a report from the wrong list correctly gives "not
entitled", so it looks like the list is wrong, not the permissions.

## Steps to reproduce
1. Firm A subscribes to Energy, Firm B to Rates. One Energy and one Rates report are published.
2. A Firm A user loads `GET /reports`, then a Firm B user loads `GET /reports` within a minute.
3. The Firm B user sees Firm A's list (the Energy report).

## Acceptance criteria
- Each firm always sees the list for its own entitlements.
- The list keeps being cached (it's our busiest endpoint) and publishing or withdrawing a report still refreshes lists.

## Notes
The 60-second cache was added in RES-090 to take load off the database.
