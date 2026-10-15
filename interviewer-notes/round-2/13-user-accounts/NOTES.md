# R2-13 · Accounts Service: interviewer notes

~465 lines. Security-flavoured: two tickets have **wrong-layer ACs**. Good candidates map each ticket to a README security rule first.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| ACC-1301 duplicate accounts | Email stored and looked up **as typed**; the UNIQUE constraint is on the raw string | `services/signup.py`, `services/auth.py`, `services/reset.py` (all call `by_email` raw) | Normalising only in signup (then login with different casing fails), or only lower-casing without `strip()`. Best: one `normalize_email()` used at every entry point, and store normalised |
| ACC-1302 reset link reuse | `reset` checks `used_at is None` but **never sets it**. Even if it did, check-then-set would race | `services/reset.py::reset`, `repositories/tokens.py` | Setting `used_at` in a separate statement after the check (two concurrent resets both pass). Accept: `UPDATE reset_tokens SET used_at=? WHERE token=? AND used_at IS NULL` + rowcount |
| ACC-1303 lockout bypassed | The lock is only checked inside the **wrong-password** branch, so a correct guess while locked succeeds (and clears the lock) | `services/auth.py::login` | **AC asks for a CAPTCHA.** That's UI hardening that doesn't fix the server-side rule in the README. The fix is moving the lock check before verification |
| ACC-1304 deleted users in search | `search_by_name` has no `deleted_at IS NULL` filter | `repositories/users.py::search_by_name` | Filtering in the service (works, but every other caller of the repo still leaks); either is acceptable if justified |

## ACC-1302 in depth
**Invariant:** each token transitions unused → used exactly once.
Deterministic test: two concurrent `reset` calls with the same token; patch `TokenRepository.get` so the first two calls wait on
`Barrier(2)`. Exactly one succeeds. Also check that sequential reuse fails.
Bonus discussion: a successful reset should invalidate **other** outstanding tokens for the user (out of scope, worth mentioning).

## ACC-1303 in depth
Ask: "With the current order, what does an attacker learn from the response when the account is locked?" With the bug, wrong passwords get 423 while
locked but the right one gets 200, so the response itself tells the attacker when they've guessed correctly. After the fix, locked accounts return 423 regardless.

## Out-of-scope smells
- Failed-attempt counting is read-modify-write (`user.failed_attempts + 1`), so concurrent bad logins can undercount. A real but separate issue; mention it.
- `request_reset` returning None for unknown e-mails is deliberate (no account enumeration).

## Strong prompts
- "For each security rule in the README, point me to the code that enforces it. Don't change code."
- "Walk me through `login` for a locked account when the password is correct."
