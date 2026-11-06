# IAM-620: Removed admins keep admin rights for several minutes

**Type:** Security · **Priority:** High · **Reporter:** Customer (Acme Corp IT)

## Description
Acme's IT team removed the admin role from a contractor on his last day. For the next several minutes, while still logged in, he
could keep creating users, and he made himself a new admin account. In our admin page his roles already showed "member" only.
Granting roles has a similar delay in some cases.

## Acceptance criteria
- After a role is granted or revoked, the user's very next request uses the new permissions.
- Permissions stay cached otherwise (they're checked on every request).
