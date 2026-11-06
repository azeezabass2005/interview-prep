# ALR-520: Full phone numbers found in logs

**Type:** Security / Privacy · **Priority:** High · **Reporter:** Data Protection Officer

## Description
A privacy audit found complete customer phone numbers in our worker logs (`delivery_sent` and `delivery_failed` lines), for
example `+44 7700 900456`. Others in the same logs are masked correctly (`+*********23`). Customers enter numbers in different
formats in the web app, and we store them as entered.

## Acceptance criteria
- No log line contains a full phone number in any common format (spaces, dashes, brackets, with or without `+`).
- Masked numbers still show the last two digits so support can tell numbers apart.
- Email masking keeps working.

## Out of scope
- Normalising numbers we already store (a separate migration, ALR-523).
