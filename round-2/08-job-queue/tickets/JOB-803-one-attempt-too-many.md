# JOB-803: Jobs attempted one more time than `max_attempts`

**Type:** Bug · **Reporter:** E-mail platform · **Priority:** Medium

## Description
A client e-mail job with `max_attempts = 3` was sent **4** times (it failed on our side after the SMTP send). We rely on `max_attempts`
as a hard limit.

## Acceptance criteria
- A job is run at most `max_attempts` times; after the last failure its status is `DEAD`.

## Out of scope
- Making the e-mail handler idempotent.
