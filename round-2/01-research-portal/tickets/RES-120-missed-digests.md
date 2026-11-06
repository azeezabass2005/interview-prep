# RES-120: Clients miss research in their daily digest

**Type:** Bug · **Priority:** High · **Reporter:** Client Services

## Description
Postbox (our email provider) had a 20-minute partial outage on Tuesday morning while the digest ran. Some clients got no digest
that day, which is expected, but Wednesday's digest didn't include Tuesday's reports either, so those clients never heard about
them. The worker dashboard shows every digest job from Tuesday as "done" with no retries, even though the worker is supposed to
retry failures.

## Steps to reproduce
1. A client with new reports since their last digest.
2. Postbox returns 503 for the send.
3. The job is marked done, and the next digest doesn't include those reports.

## Acceptance criteria
- If the email can't be sent, the job is retried by the worker (it already supports retries with backoff).
- A report is only considered "sent" to a user once their digest email was actually accepted by Postbox.
- A user gets each report in a digest once, not twice.
