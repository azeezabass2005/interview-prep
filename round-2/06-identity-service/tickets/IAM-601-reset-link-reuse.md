# IAM-601: Password reset links can be used more than once

**Type:** Security · **Priority:** Critical · **Reporter:** Penetration test (external)

## Description
The pen testers requested a reset, used the link to set a new password, then used the **same link** again 10 minutes later and set
a different password. Reset emails sit in mailboxes (and sometimes in shared inboxes or forwarded threads), so anyone who later sees
an old email within the 30 minutes can take over the account.

## Acceptance criteria
- A reset link can be used successfully only once; any later use is refused (401) and doesn't change the password.
- This holds even if two requests use the same link at the same moment.
- Expired links are still refused.
