# EDGE-905: Requests can't be traced from the gateway to the services

**Type:** Bug · **Priority:** Medium · **Reporter:** SRE

## Description
During last week's incident we had the request id of every failing request from the gateway's logs (`X-Request-ID`), but none of
those ids appear in the orders or quotes services' logs: each service generates its own. Tracing a single request across services
took hours of matching timestamps. Customers who send their own `X-Request-ID` say support can't find their requests either.

## Acceptance criteria
- Every upstream request carries the same `X-Request-ID` the gateway uses (the client's, or the one the gateway generated).
- The response to the client still has that request id.
