# News Feed Aggregator

Ingests stories from wire services and partner sites, de-duplicates them, ranks them, and serves a paged feed to the terminal's
news panel. Ingestion workers and API instances share one database.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
newsfeed/api/handlers.py             NewsApi: ingest, feed, tag search
newsfeed/services/ingest.py          IngestService: normalise URL, de-duplicate, store
newsfeed/services/urls.py            canonical URL rules
newsfeed/services/ranking.py         score = source weight × time decay
newsfeed/services/feed.py            FeedService: ranked feed pages, tag filter
newsfeed/repositories/stories.py     stories + story_tags tables
newsfeed/sources.py                  source weights
newsfeed/db.py, clock.py, errors.py, models.py, config.py
```

## Rules

- **De-duplication:** two stories are the same if their **canonical URLs** match. Canonical URL: lower-case scheme and host, drop
  `www.`, drop the fragment, drop tracking parameters (`utm_*`, `ref`, `cmpid`), drop a trailing `/` from the path, keep other query
  parameters sorted.
- **Ranking:** `score = source_weight × 0.5 ^ (age_hours / 6)`, so a story's score halves every **6 hours**.
- **Feed pages:** `GET /feed?cursor=…&limit=n`. While a user pages through, newly ingested stories must not cause items to be **skipped or
  repeated**. The feed is ordered by publish time (newest first) and the cursor marks the last story seen.
- **Tags** are case-insensitive (`Fed`, `FED`, `fed` are the same tag).
