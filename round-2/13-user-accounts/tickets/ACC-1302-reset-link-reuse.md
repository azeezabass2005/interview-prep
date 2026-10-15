# ACC-1302: Password reset link works more than once

**Type:** Bug (security) · **Reporter:** Penetration test report · **Priority:** Critical

## Description
The pen-testers reused a password reset link after it had already been used, and set a new password. Anyone who finds an old reset e-mail
can take over the account within the hour.

## Acceptance criteria
- A reset token can be used successfully at most once, including when two requests use it at the same time.
- Expired tokens (older than 1 hour) are rejected.

## Out of scope
- Rate-limiting reset e-mails.
