# GW-1203: Clients told to wait 15 s, get 429 again; told 45 s, could have retried sooner

**Type:** Bug · **Reporter:** Partner engineering · **Priority:** Low

## Description
Well-behaved clients honour `Retry-After`, but the value looks wrong. When they hit the limit 15 s into a minute they're told to wait
15 s (should be 45 s); at 45 s into a minute they're told to wait 45 s (should be 15 s).

## Acceptance criteria
- `Retry-After` is the number of seconds until the current window ends (rounded up, at least 1).

## Out of scope
- Jitter.
