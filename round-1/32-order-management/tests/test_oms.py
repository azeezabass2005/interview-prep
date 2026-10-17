import unittest

from oms import OrderManager


class TestOms(unittest.TestCase):
    def test_full_fill(self):
        oms = OrderManager()
        oms.submit("o1", "acc", "ABC", "BUY", 100, "10.00")
        self.assertEqual(oms.execute("e1", "o1", 100, "10.00").status, "FILLED")


if __name__ == "__main__":
    unittest.main()
