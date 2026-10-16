from collections import Counter

from .services.grading import course_percent, letter
from .store import InMemoryStore


def distribution(store: InMemoryStore, course_id: str) -> dict:
    course = store.course(course_id)
    return dict(sorted(Counter(letter(course_percent(course, s)) for s in course.students).items()))
