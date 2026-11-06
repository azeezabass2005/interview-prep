# R2-06 · Accounts (identity service): Interviewer Guide

A ~700-line Python identity service (no framework): users, PBKDF2 passwords, sessions with sliding expiry, password resets by
email, login lockout, and cached role-based permissions. Every ticket is an authentication/authorization bug that a security
review would flag. The candidate picks one; one ticket done properly with a test is a full pass. `web/` is context only.

## Ticket map

| Ticket | Area | Real root cause | Where | Trap |
|---|---|---|---|---|
| IAM-601 reset link reuse | Authentication | `confirm_reset` checks `used_at` but never sets it; `ResetTokenRepository.mark_used` exists (atomic `WHERE used_at IS NULL`) and is never called | `services/auth.py: confirm_reset` | Calling `mark_used` *after* changing the password and ignoring its result (two concurrent uses both succeed); deleting the row |
| IAM-605 sessions never expire | Authentication / sessions | Sliding expiry is extended forever; `SESSION_ABSOLUTE_HOURS` is defined but never used | `services/auth.py: authenticate` (and `login`) | Shortening the idle timeout; checking `created_at` only at login |
| IAM-610 lockout bypass | Rate limiting | Throttle key is `email.strip()` (case-sensitive) while the user lookup is case-insensitive | `services/auth.py: login` | Lower-casing only in the throttle (fine) vs. in some places and not others; keying by user id (unknown emails then aren't throttled) |
| IAM-615 account enumeration | Error handling / security | Unknown email → `NotFound` (404 "no account…"); wrong password → 401 "wrong password" | `services/auth.py: login` | Changing only the status code and keeping different messages; stopping throttling for unknown emails |
| IAM-620 revoked admin | Caching / authorization | `PermissionService` caches permissions for 10 min; `grant`/`revoke` don't invalidate | `services/permissions.py` | Turning the cache off (AC says keep it); shortening the TTL (still a window) |

## PM answers
| Question | Answer |
|---|---|
| Can two people use one reset link? | No: one successful use, ever. |
| Is the 12-hour limit from login or from the last password change? | From login (session creation). |
| After 12 hours, what does the user see? | 401; the web app sends them to sign in. |
| What error should a failed login show? | `401`, "invalid email or password", for every failure reason. |
| Is lockout per account or per IP? | Per account (email). An IP limiter already exists in front. |
| How quickly must revocation apply? | The next request. |
| Multiple API instances? | Yes. Note the cache is per instance (bonus discussion). |

## IAM-601 · single-use reset links
**Fix:** after validating, `if not self._resets.mark_used(token_hash, now): raise Unauthorized(...)`, *before* changing the password
(the conditional UPDATE is the atomic claim).
**Test:** request a reset, confirm with password A (204), confirm again with password B → 401; log in with A works, B doesn't.

## IAM-605 · absolute lifetime
**Fix:** cap expiry at `created_at + SESSION_ABSOLUTE_HOURS`: in `authenticate`, refuse when `now >= created + 12h`, and extend to
`min(now + idle, created + 12h)`.
**Test:** request every 20 minutes; at 11:40 still 200; past 12:00 → 401. Idle expiry test still passes.

## IAM-610 · normalise the throttle key
**Fix:** `key = email.strip().lower()`.
**Test:** 5 failures with different capitalisations, then the right password with any capitalisation → 429.

## IAM-615 · uniform failure
**Fix:** unknown email → `Unauthorized("invalid email or password")`, and use the same message for wrong password/disabled.
**Test:** unknown email and wrong password → same status (401) and same `error` body (except `request_id`). Strong: mentions the
timing side channel (PBKDF2 only runs for known users: compare against a dummy hash, IAM-616).

## IAM-620 · invalidate on change
**Fix:** `self._cache.delete(user_id)` in `grant` and `revoke` (after the DB write).
**Test:** grant Ben admin; Ben lists users (200, now cached); revoke; Ben's next request → 403. Strong: notes each API instance has its
own cache, so invalidating locally isn't enough in production (versioned permissions on the session, a shared cache, or pub/sub);
the honest fix within this codebase plus naming the remaining risk is a great answer.

## Red herrings
- `check_password` uses `compare_digest`: correct.
- `request_reset` deliberately returns 202 for unknown emails.
- The IP rate limiter runs before authentication on purpose (it protects login).

## Questions about the candidate's fixes (data structures)
- "Why store a hash of the session token instead of the token?" (A DB leak doesn't give working sessions; lookup by hash is still O(1)
  with the primary key.)
- "The throttle is an in-memory dict per instance. With 4 instances, how many guesses?" (Up to 4×5 per window. Shared store with
  atomic increments; or count failures in the DB.)
- "The throttle's dict grows with every email ever tried. Fix?" (Prune on access (done for one key), periodic sweep, or a TTL store.)
- "How would you revoke all sessions for a user quickly?" (Index on `user_id`; `revoke_all` exists. Or a per-user `sessions_valid_after`
  timestamp checked at authentication.)

## Feature requests
1. **"Remember me for 30 days on trusted devices."** Strong: a separate long-lived refresh token, rotation on use, reuse detection,
   device binding, revocation list; doesn't relax SP-7 for normal sessions.
2. **"Two-factor authentication with TOTP."** Strong: secret enrolment flow, ±1 step window, replay protection (store last used
   step), recovery codes hashed, throttling on codes.
3. **"SSO with the customer's identity provider (SAML/OIDC)."** Strong: per-org configuration, JIT provisioning, mapping IdP groups to
   roles, and what happens to local passwords.

## Scoring signals
- **Strong:** thinks like an attacker (two concurrent uses, case variants, response diffing); writes the exploit as a test first;
  keeps behaviour for legitimate users; names residual risks (multi-instance cache, timing).
- **Weak:** removes the cache; changes timeouts; fixes the symptom in the web app; no negative test (only checks the happy path).
