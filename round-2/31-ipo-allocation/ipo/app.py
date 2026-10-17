from .api import IpoApi
from .services.book import BookService
from .services.closing import ClosingService
from .store import InMemoryStore


def build_app():
    book = BookService(InMemoryStore())
    return IpoApi(book, ClosingService(book))
