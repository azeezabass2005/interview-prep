# MKT-320: Error dashboard showed 0% while customers saw 502s

**Type:** Bug · **Priority:** High · **Reporter:** SRE

## Description
During Tickstream's 40-minute maintenance window yesterday, customers got `502` on every quote request, but our error-rate
dashboard stayed at 0% and nobody was paged. The access logs from that window have only `200`s; the failed requests aren't in the
logs at all. We also never see `401` or `429` in the dashboard, which is suspicious.

## Acceptance criteria
- Every request is counted in `http_requests_total` with the status code the client actually received (including 4xx and 5xx),
  and has an access-log line.
- Error responses keep their current shape and status codes.
