# Short Links Service

Internal URL shortener used by marketing, research and client services (`bbg.link/abc123`). Users create short links with either a
generated code or a custom **alias**; visitors are redirected; owners see click counts. Several redirect instances share one database.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
shortlinks/api/handlers.py          LinkApi: create, redirect, info
shortlinks/services/links.py        LinkService: create / resolve / info
shortlinks/services/analytics.py    ClickRecorder: click events + counters
shortlinks/services/validation.py   URL / alias validation
shortlinks/codes.py                 random code generation
shortlinks/abuse.py                 blocked destination domains
shortlinks/repositories/links.py    links + click_events tables
shortlinks/db.py, clock.py, errors.py, models.py, config.py
```

## Rules

- Generated codes are 6 characters from `[a-z0-9]`. A code or alias, once assigned, **must never point anywhere else**.
- Aliases are **case-insensitive**: `Promo`, `promo` and `PROMO` are the same alias, so only one can exist.
- Links may have an expiry. An **expired** link returns **410 Gone** on redirect.
- Every redirect records a click event and increments the link's `clicks` counter. The counter must equal the number of redirects.
