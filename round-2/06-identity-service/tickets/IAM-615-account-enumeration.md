# IAM-615: Login tells attackers which emails have accounts

**Type:** Security · **Priority:** Medium · **Reporter:** Bug bounty report

## Description
`POST /login` answers `404 "no account with that email"` for unknown addresses and `401 "wrong password"` for known ones. The
reporter used this to check a list of 50,000 leaked emails and found which of them are our customers. The password-reset endpoint
already avoids this.

## Acceptance criteria
- A login with an unknown email and a login with a wrong password get the same status code and the same error body.
- Failed logins for unknown emails still count towards the lockout for that email.

## Out of scope
- Equalising response times (tracked separately, IAM-616).
