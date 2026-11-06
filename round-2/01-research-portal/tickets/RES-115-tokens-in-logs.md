# RES-115: Client access tokens found in the log pipeline

**Type:** Security · **Priority:** Critical · **Reporter:** Security Engineering

## Description
A scan of last week's API logs found 1,812 bearer tokens in plain text. All of them are on `request` log lines for
`/reports/{id}/pdf`. Anyone with log access could have replayed them until they expired. The tokens have been rotated; we need to
stop logging them.

## Acceptance criteria
- No credential (header or query parameter) appears in any log line.
- Access logs keep everything else they log today (method, path, status, duration, request id, other query parameters), so the
  dashboards that use them keep working.
- PDF links with `?access_token=` keep working for the web app.

## Out of scope
- Replacing query-string tokens with short-lived signed download URLs (tracked as RES-118).
