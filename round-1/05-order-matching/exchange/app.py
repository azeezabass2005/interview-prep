from .api import ExchangeApi
from .engine import MatchingEngine


def build_app():
    engine = MatchingEngine()
    return ExchangeApi(engine), engine
