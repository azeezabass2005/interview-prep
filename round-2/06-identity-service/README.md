# Accounts (identity service)

Every customer-facing app signs in through this service. It owns users, passwords, login sessions, password resets and roles,
and the other services ask it who a session belongs to and what they may do. The account pages (`web/`) are a Next.js app.
Several instances run behind a load balancer and share one database; reset emails go through **Postbox**.

You'll investigate one reported problem from `tickets/`, make a bounded change, and prove it with a test.
Completion percentage is not the signal: one ticket done properly is a full pass.

## Running

```bash
python -m unittest discover -s tests -v      # the test suite (standard library only)
python -m identity.seed && python server.py  # demo accounts, then the API on :8000
cd web && npm install && npm run dev         # optional: the account pages on :3000
```

## Architecture

```text
identity/
  wiring.py                  builds the app; public paths (login, password reset) skip authentication
  services/auth.py           login, session validation (sliding expiry), logout, password reset
  services/throttle.py       locks an account after repeated failed logins
  services/permissions.py    roles -> permissions, cached per user
  repositories/accounts.py   SQL for users, roles, sessions, reset tokens
  passwords.py               PBKDF2 hashing and password rules
  adapters/postbox.py        Postbox email client
  config.py                  session lifetimes, lockout, cache and role definitions
  api/handlers.py            endpoints, including /admin for organisation admins
  middleware.py, cache.py, db.py, app.py, router.py, http.py, observability.py, ratelimit.py, clock.py, ids.py, errors.py
web/                         Next.js account pages (you shouldn't need to change them)
```

## Security requirements (security policy SP-7)

- Email addresses are case-insensitive.
- Sessions expire after **30 minutes** without activity, and after **12 hours** at most, however active the user is.
- After **5 failed logins** within 15 minutes, an account is locked for the rest of the window.
- Login and password-reset responses must not reveal whether an email address has an account.
- A password-reset link works **once**, for 30 minutes. Resetting a password signs the user out everywhere.
- Role changes take effect **immediately**. Permissions may be cached, but never served after they've changed.
