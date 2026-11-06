# IAM-610: Account lockout can be bypassed

**Type:** Security · **Priority:** High · **Reporter:** Penetration test (external)

## Description
After 5 wrong passwords for `ben@acme.example` the account locks, as designed. But the testers kept guessing by changing the
capitalisation of the email (`Ben@acme.example`, `BEN@ACME.EXAMPLE`, …), getting 5 more guesses each time, and their
password-guessing script could keep going indefinitely.

## Acceptance criteria
- Failed logins for an account count towards the same limit however the email is written.
- Locking still expires after the 15-minute window; a successful login still resets the count.
