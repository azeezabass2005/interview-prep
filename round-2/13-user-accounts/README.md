# Accounts Service

Sign-up, login, password reset and the people directory for a client portal. Several API instances share one database.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
accounts/api/handlers.py           AccountsApi
accounts/services/signup.py        SignupService
accounts/services/auth.py          AuthService.login (with lockout)
accounts/services/reset.py         PasswordResetService
accounts/services/directory.py     people search
accounts/services/passwords.py     PBKDF2 hashing
accounts/repositories/*.py         users, reset_tokens
accounts/audit.py                  security audit log
accounts/db.py, clock.py, errors.py, models.py, config.py
```

## Security rules

- **E-mail addresses identify accounts** and are compared **case-insensitively, ignoring surrounding whitespace**. One account per address.
- **Lockout:** after **5 consecutive failed logins**, the account is locked for **15 minutes**. While locked, **every** login attempt is
  rejected, even with the right password. A successful login resets the failure count.
- **Password reset tokens** are valid for **1 hour** and can be used **once**.
- **Deleted** accounts (soft-deleted, `deleted_at` set) never appear in the directory and can't log in.
