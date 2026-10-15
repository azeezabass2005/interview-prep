# CAL-TICKET-stuck-pending: Some requests stay PENDING forever

**Type:** Bug · **Reporter:** Chief of Staff · **Priority:** Medium

## Description
After the nightly batch, a few requests are neither scheduled nor marked unschedulable: they just stay `PENDING`, and they're
not always the same ones. On quiet days (a handful of requests) everything works. On busy days several get stuck.

## Steps to reproduce
1. Submit 6 requests that easily fit on Tuesday.
2. Run the batch for Tuesday.
3. Only 4 meetings are scheduled; 2 requests are still `PENDING`.

## Acceptance criteria
- After `run_batch(day)`, no request whose window is on that day is left `PENDING`.
- Requests are still processed highest score first.

## Out of scope
- Changing `BATCH_SIZE`.
