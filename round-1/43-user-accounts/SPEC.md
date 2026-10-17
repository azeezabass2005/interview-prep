# User Accounts

The sign-up, login and password-reset logic of a web app. `accounts.py` holds the users and the authentication rules.

## Sign-up

- E-mail addresses are unique **ignoring case and surrounding spaces** (`Ana@X.com ` and `ana@x.com` are the same).
- Passwords: at least **12** characters, at least one letter and one digit, and must **not contain the e-mail's local part** (the bit
  before `@`), ignoring case.
- Passwords are stored as salted PBKDF2 hashes, never in plain text.

## Login

- Wrong password → failure. **5 consecutive** failures lock the account for **15 minutes**; while locked, even the right password fails.
- A successful login resets the failure count.

## Password reset

- `request_reset` issues a token valid for **30 minutes**. Requesting a new token invalidates earlier ones.
- A token can be used **once**. Using it sets a new password (same rules), and **unlocks** the account (clears failures and any lock).

## Example

Ana signs up with `ana@example.com` / `correct-horse-42`. She logs in with a wrong password 5 times → locked. She resets her password
→ she can log in **immediately** with the new password.
