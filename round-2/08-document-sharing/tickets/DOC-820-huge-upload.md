# DOC-820: A 200 MB upload took down an API instance

**Type:** Bug · **Priority:** High · **Reporter:** SRE

## Description
An instance ran out of memory and restarted. The last request it logged was a 200 MB `POST /documents` from a script using
chunked transfer encoding, so the request had no `Content-Length` header. Our 1 MB limit didn't stop it. Security points out a
client can also simply send a small `Content-Length` with a large body.

## Acceptance criteria
- Any request whose body is over 1 MB gets `413`, whatever the headers say.
- Normal requests are unaffected.

## Out of scope
- Streaming the limit at the socket level in `server.py` (Platform team will do that in the load balancer).
