# LNK-703: Expired links still redirect

**Type:** Bug · **Reporter:** Compliance · **Priority:** High

## Description
Links to time-limited research previews are created with an expiry. The info page shows them as expired, but visiting the link still
redirects to the (now confidential) document.

## Acceptance criteria
- Redirecting an expired link returns 410 and records no click.
- Links without expiry, or not yet expired, still redirect.

## Out of scope
- Deleting expired links.
