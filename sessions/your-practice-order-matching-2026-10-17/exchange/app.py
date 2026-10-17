from .api import ExchangeApi
from .engine import MatchingEngine


def build_app():
    # Create a matching engine and return it alongside its API facade.
    engine = MatchingEngine()
    return ExchangeApi(engine), engine
