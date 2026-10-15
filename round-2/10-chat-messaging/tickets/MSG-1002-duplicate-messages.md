# MSG-1002: Same message shows twice after a network blip

**Type:** Bug · **Reporter:** Mobile team · **Priority:** Medium

## Description
On bad networks the app retries a send while the first attempt is still in flight (same `client_msg_id`). The conversation then shows
the message twice. Sequential retries are fine.

## Acceptance criteria
- Overlapping sends with the same sender, conversation and `client_msg_id` store exactly one message; both calls return it.
- Two different senders may use the same `client_msg_id`.

## Out of scope
- Client retry policy.
