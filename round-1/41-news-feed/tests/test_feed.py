import unittest
from datetime import datetime

from feed import NewsFeed

NOW = datetime(2026, 5, 4, 12, 0)


class TestFeed(unittest.TestCase):
    def test_followed_ticker(self):
        f = NewsFeed()
        f.follow("ana", tickers=["AAPL"])
        f.add("a1", "reuters", "Apple beats estimates", datetime(2026, 5, 4, 9, 0), ["AAPL"])
        f.add("a2", "reuters", "Oil rises", datetime(2026, 5, 4, 9, 5), ["XOM"])
        items, _ = f.page("ana", NOW)
        self.assertEqual([a.article_id for a in items], ["a1"])


if __name__ == "__main__":
    unittest.main()
