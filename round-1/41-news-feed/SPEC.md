# News Feed

A financial news aggregator builds a personal feed for each user from many news sources. `feed.py` stores articles and builds feed pages.

## Articles

An article has an id, source, headline, publish time and the tickers it mentions. Articles with a publish time in the **future** are
embargoed: they don't appear until their publish time.

## What a user sees

- Articles from a **followed source**, or mentioning a **followed ticker**.
- Never articles from a **muted source**, even if they mention a followed ticker.
- **Syndication dedupe:** the same story often arrives from several sources. Two articles are the same story if their headlines match
  after lower-casing and collapsing runs of whitespace (and trimming), and they were published **within 24 hours** of each other. Only the
  **earliest** one is shown.

## Pages

Newest first; ties on publish time by article id, descending. `page(user, now, limit, cursor)` returns up to `limit` articles and a cursor;
the next page continues **strictly after** the last article returned, so no article is skipped or repeated.

## Other operations

- `unfollow` removes tickers/sources from a user's preferences, and can unmute sources.
- `search(user, now, text)`: articles from the user's feed (same rules) whose normalised headline contains every word of the text.
- `source_counts(user, now)`: how many feed articles came from each source, most first (ties alphabetical).

## Example

Ana follows AAPL and mutes `spamwire`. 09:00 Reuters "Apple beats estimates" (AAPL) · 09:05 spamwire "AAPL to the moon" (AAPL) ·
09:30 Bloomberg "Apple  beats estimates" (AAPL). Ana's feed: **only the 09:00 Reuters article**.
