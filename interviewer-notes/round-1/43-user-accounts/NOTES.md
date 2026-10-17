# R1-43 · User Accounts: Interviewer Guide

The Round 1 version of Round 2 #13. One file, `accounts.py` (~90 lines), with one passing test. **The spec example fails on the buggy
code** (B5: still locked after the reset).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Local part shorter than 3 chars (`al@…`) | Still applies. |
| Token at exactly 30 minutes | Expired. |
| Login attempts while locked | Don't extend the lock. |
| Reset for an unknown e-mail | Same response as success (don't leak) — out of scope here. |
| Do failures expire over time? | No; only success or reset clears them. |

## Code map
`_key` · `_check_password` · `sign_up` · `_user` · `login` (lock) · `request_reset` · `reset`.

## Planted bugs (5)

### B1 · E-mail case-sensitive
- **Where:** `_key`.
- **Test:** `ANA@example.com` after `ana@example.com` → refused.

### B2 · Local-part rule missing
- **Where:** `_check_password` receives `email` and never uses it (clue).
- **Test:** `bob@…` with `xxBOB12345678` → refused.

### B3 · Failures not reset on success
- **Where:** `login`.
- **Test:** 4 fails, success, 4 fails → still able to log in.

### B4 · Token reusable
- **Where:** `reset` never clears `tokens`.
- **Test:** second use of the same token → refused.

### B5 · Reset doesn't unlock
- **Where:** `reset`.
- **Test:** locked, reset → login with the new password **succeeds** immediately.

Hints: (1) "which parameter is unused?"; (2) "the spec example is a 3-step story: test it end to end".

## Red herrings
- `hmac.compare_digest`: correct (constant-time).
- New token invalidates older ones (`tokens = {…}`): correct.

## Questions about the candidate's fixes (data structures)
- **Users dict keyed by normalised e-mail:** "Why normalise in exactly one function?" (One source of truth: B1 shows why.)
- **Tokens:** "Stored in plain text in memory. In a DB?" (Store a hash of the token; compare hashes.) "Why `secrets` and not `random`?" (CSPRNG.)
- **Lockout as a DoS vector:** "Anyone can lock Ana out by guessing wrong. Alternatives?" (Per-IP + per-account throttling; exponential backoff; CAPTCHA.)
- **PBKDF2 iterations:** "Why so few here, and what in production?" (Test speed; hundreds of thousands, or bcrypt/argon2.)

## Feature requests
1. **"Two-factor authentication with TOTP."** Strong answer: shared secret; 30-s windows ±1; replay protection (last used step).
2. **"Password history: can't reuse the last 5."** Strong answer: keep hashes with their salts; compare each; bounded deque.
3. **"Notify the user by e-mail on lockout."** Strong answer: event on lock; outbox; rate-limit notifications.

## Scoring signals
- **Strong:** tests the example as a story; probes case/whitespace; thinks about security consequences.
- **Weak:** only sign-up + correct login.
