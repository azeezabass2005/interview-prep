# MKT-305: Quotes are stale for half an hour

**Type:** Bug · **Priority:** Critical · **Reporter:** Trading Desk (Alder Partners)

## Description
Alder's traders noticed AAPL in their tool sitting at the same price for about 30 minutes while it moved on every other screen.
Restarting their tool didn't help; it changes on its own after a while. Our Tickstream bill is also much lower than usual this
month, which fits: we're hardly calling them.

## Acceptance criteria
- A latest quote is never served more than 2 seconds after we fetched it.
- We still cache within those 2 seconds (Tickstream bills per request).

## Out of scope
- Streaming quotes over WebSockets.
