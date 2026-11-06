# IAM-605: Active sessions never expire

**Type:** Security · **Priority:** High · **Reporter:** Security Engineering (audit against SP-7)

## Description
The audit found sessions more than 3 days old still in use: a trading-floor dashboard that polls every minute has kept the same
session since Monday. SP-7 says a session lives at most 12 hours, however active it is. Idle expiry (30 minutes) works.

## Acceptance criteria
- A session is refused once it's 12 hours old, even with continuous activity.
- Idle expiry (30 minutes without activity) keeps working, and activity still extends a session up to the 12-hour limit.
