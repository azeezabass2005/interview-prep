from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import FrozenSet, Set

DEDUPE_WINDOW = timedelta(hours=24)


class FeedError(Exception):
    pass


@dataclass(frozen=True)
class Article:
    article_id: str
    source: str
    headline: str
    published_at: datetime
    tickers: FrozenSet[str]


@dataclass
class Prefs:
    tickers: Set[str] = field(default_factory=set)
    sources: Set[str] = field(default_factory=set)
    muted: Set[str] = field(default_factory=set)


def normalise(headline):
    return headline.strip().lower()


class NewsFeed:
    def __init__(self):
        self.articles = {}
        self.prefs = {}

    def add(self, article_id, source, headline, published_at, tickers=()):
        if article_id in self.articles:
            raise FeedError("duplicate article id")
        self.articles[article_id] = Article(article_id, source, headline, published_at, frozenset(tickers))

    def follow(self, user, tickers=(), sources=(), muted=()):
        p = self.prefs.setdefault(user, Prefs())
        p.tickers |= set(tickers)
        p.sources |= set(sources)
        p.muted |= set(muted)

    def _matches(self, prefs, a):
        if a.source in prefs.sources:
            return a.source not in prefs.muted
        return bool(a.tickers & prefs.tickers)

    def _visible(self, user, now):
        prefs = self.prefs.get(user, Prefs())
        matched = [a for a in self.articles.values() if self._matches(prefs, a)]
        kept = {}
        for a in sorted(matched, key=lambda a: a.published_at):
            key = normalise(a.headline)
            first = kept.get(key)
            if first is None or a.published_at - first.published_at > DEDUPE_WINDOW:
                kept[key] = a
            else:
                kept[key] = a
        return sorted(kept.values(), key=lambda a: (a.published_at, a.article_id), reverse=True)

    def page(self, user, now, limit=20, cursor=None):
        items = self._visible(user, now)
        if cursor is not None:
            items = [a for a in items if a.published_at < cursor[0]]
        chosen = items[:limit]
        next_cursor = (chosen[-1].published_at, chosen[-1].article_id) if len(chosen) == limit else None
        return chosen, next_cursor

    def unfollow(self, user, tickers=(), sources=(), unmute=()):
        p = self.prefs.setdefault(user, Prefs())
        p.tickers -= set(tickers)
        p.sources -= set(sources)
        p.muted -= set(unmute)

    def search(self, user, now, text, limit=20):
        words = normalise(text).split()
        hits = [a for a in self._visible(user, now) if all(w in normalise(a.headline) for w in words)]
        return hits[:limit]

    def source_counts(self, user, now):
        counts = {}
        for a in self._visible(user, now):
            counts[a.source] = counts.get(a.source, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
