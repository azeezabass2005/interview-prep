from .api import AuctionApi
from .services.bidding import BiddingService
from .services.closing import ClosingService
from .store import InMemoryStore


def build_app(clock):
    store = InMemoryStore()
    bidding = BiddingService(store, clock)
    return AuctionApi(store, bidding, ClosingService(store, bidding, clock)), store
