# ACC-1303: Attacker logged in after 40 failed attempts

**Type:** Bug (security) · **Reporter:** Security operations · **Priority:** Critical

## Description
The audit log shows 40 failed logins for one account in 6 minutes, then a successful login from the same IP. The account should have been
locked after 5 failures.

## Acceptance criteria
- Add a CAPTCHA to the login page after 3 failed attempts.
- After 5 consecutive failures, no login succeeds for 15 minutes.

## Out of scope
- IP-based blocking.
