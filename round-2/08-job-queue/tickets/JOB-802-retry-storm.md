# JOB-802: Failing jobs hammer the downstream API

**Type:** Bug · **Reporter:** Pricing API team · **Priority:** Medium

## Description
When our API is down, export jobs retry far too aggressively at first and then wait much too long. The fourth retry waited 4 minutes,
but the first retries came in a burst. We were promised exponential back-off.

## Acceptance criteria
- Retry delays are 30, 60, 120, 240, 480 seconds…, never more than 600 s.

## Out of scope
- Jitter.
