# JOB-804: Scheduled jobs run hours early

**Type:** Bug · **Reporter:** Research distribution · **Priority:** High

## Description
We schedule research publication jobs for 09:00 New York time by sending `run_at: "2026-05-01T09:00:00-04:00"`. They ran at 05:00 New York
time, before the embargo lifted. Teams in London (`+01:00`) report jobs running an hour **late**.

## Acceptance criteria
- A job never starts before the instant given in `run_at`, whatever offset the client used.
- `GET /jobs/{id}` returns `run_at` in UTC.

## Out of scope
- Daylight-saving rules in the clients.
