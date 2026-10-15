# MD-302: Vendor rate limit exceeded at market open

**Type:** Bug · **Reporter:** Market data engineering · **Priority:** High

## Description
At 09:30 hundreds of screens request the same symbols in the same instant. The vendor reports bursts of up to 200 identical calls for one
symbol from a single instance within a few milliseconds, and throttles us for a minute. During that minute everyone gets stale fallback
prices.

## Steps to reproduce
1. Cold cache (or right after an entry expires).
2. 50 concurrent `GET /quotes/AAPL` to one instance.
3. Metrics show `vendor_calls` = 50.

## Acceptance criteria
- For concurrent requests for the **same symbol on one instance**, the vendor is called **once**; all callers get that quote.
- Requests for **different symbols** are not serialised behind each other.
- Behaviour across instances is unchanged (each instance still fetches once).

## Out of scope
- A shared cache across instances.
