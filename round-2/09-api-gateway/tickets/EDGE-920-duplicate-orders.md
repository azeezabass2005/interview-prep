# EDGE-920: Duplicate orders when the orders service is slow

**Type:** Bug · **Priority:** Critical · **Reporter:** Trading Operations

## Description
During yesterday's slowdown of the orders service, 37 customers had the same order placed twice or three times. Each customer
sent one `POST /v1/orders`. The orders service logs show each duplicate arrived from the gateway a few seconds after the first, and
the first one had actually succeeded. Most of those customers don't send an `Idempotency-Key`.

## Acceptance criteria
- The gateway never sends a request that isn't safe to repeat more than once.
- Safe requests (GET and friends, or anything with an `Idempotency-Key`) are still retried on failures.
- When a non-retryable request fails, the client gets an error, as today.
