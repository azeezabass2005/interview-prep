from .api import GradebookApi
from .services.course import CourseService
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    return GradebookApi(CourseService(store)), store
