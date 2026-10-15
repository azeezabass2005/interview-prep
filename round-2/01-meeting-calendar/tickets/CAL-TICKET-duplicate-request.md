# CAL-TICKET-duplicate-request: Same meeting request appears twice after client retries

**Type:** Bug · **Reporter:** Executive Assistants (mobile app team) · **Priority:** High

## Description
The EA mobile app retries `POST /meeting-requests` when the network is flaky. It always sends the same `Idempotency-Key` for a retry.
Since we scaled to three service instances, Blike's queue sometimes shows **two identical requests**, and the requester gets two
"request received" emails. Both copies get scheduled, so Blike ends up with the same meeting twice.

## Steps to reproduce
1. Send `POST /meeting-requests` with `X-Requester: ea-app` and `Idempotency-Key: 7f3a…`.
2. Before the first call returns, send the same request again (it lands on a different instance).
3. Two request IDs come back; `GET /schedule` later shows both meetings.

Sequential retries (the second call after the first finished) work fine.

## Acceptance criteria
- One requester + one idempotency key results in exactly **one** stored request, even when calls overlap.
- Overlapping retries return the **same request ID** with a successful response.
- Different requesters may reuse the same idempotency key and get separate requests.

## Out of scope
- Scheduling and scoring behaviour.
- The duplicate email (it disappears once the duplicate request does).
