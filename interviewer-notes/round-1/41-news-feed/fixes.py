FIXES = [
    ("feed.py", "    return headline.strip().lower()", "    return \" \".join(headline.lower().split())"),
    ("feed.py", "        if a.source in prefs.sources:\n            return a.source not in prefs.muted\n        return bool(a.tickers & prefs.tickers)",
     "        if a.source in prefs.muted:\n            return False\n        return a.source in prefs.sources or bool(a.tickers & prefs.tickers)"),
    ("feed.py", "            else:\n                kept[key] = a\n", ""),
    ("feed.py", "        matched = [a for a in self.articles.values() if self._matches(prefs, a)]",
     "        matched = [a for a in self.articles.values() if a.published_at <= now and self._matches(prefs, a)]"),
    ("feed.py", "            items = [a for a in items if a.published_at < cursor[0]]",
     "            items = [a for a in items if (a.published_at, a.article_id) < cursor]"),
]
