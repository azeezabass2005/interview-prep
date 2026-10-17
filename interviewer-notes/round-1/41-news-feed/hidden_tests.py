import unittest
from datetime import datetime, timedelta

from feed import NewsFeed

NOW = datetime(2026, 5, 4, 12, 0)


def at(h, m=0):
    return datetime(2026, 5, 4, h, m)


def ids(items):
    return [a.article_id for a in items]


class HiddenFeed(unittest.TestCase):
    def test_B1_muted_source_excluded_for_tickers(self):
        f = NewsFeed()
        f.follow("ana", tickers=["AAPL"], muted=["spamwire"])
        f.add("s1", "spamwire", "AAPL to the moon", at(9), ["AAPL"])
        self.assertEqual(f.page("ana", NOW)[0], [])

    def test_B2_earliest_copy_kept(self):
        f = NewsFeed()
        f.follow("ana", tickers=["AAPL"])
        f.add("r1", "reuters", "Apple beats estimates", at(9), ["AAPL"])
        f.add("b1", "bloomberg", "Apple beats estimates", at(10), ["AAPL"])
        self.assertEqual(ids(f.page("ana", NOW)[0]), ["r1"])

    def test_B3_cursor_with_equal_times(self):
        f = NewsFeed()
        f.follow("ana", tickers=["X"])
        for i in (1, 2, 3):
            f.add(f"a{i}", "reuters", f"story {i}", at(9), ["X"])
        first, cursor = f.page("ana", NOW, limit=2)
        second, _ = f.page("ana", NOW, limit=2, cursor=cursor)
        self.assertEqual((ids(first), ids(second)), (["a3", "a2"], ["a1"]))

    def test_B4_embargoed_articles_hidden(self):
        f = NewsFeed()
        f.follow("ana", tickers=["X"])
        f.add("e1", "reuters", "Earnings", NOW + timedelta(hours=1), ["X"])
        self.assertEqual(f.page("ana", NOW)[0], [])

    def test_B5_whitespace_collapsed(self):
        f = NewsFeed()
        f.follow("ana", tickers=["X"])
        f.add("r1", "reuters", "Fed holds rates", at(9), ["X"])
        f.add("b1", "bloomberg", "  fed  HOLDS rates ", at(9, 30), ["X"])
        self.assertEqual(len(f.page("ana", NOW)[0]), 1)
