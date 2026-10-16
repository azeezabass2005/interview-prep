from typing import Dict, Optional

from .models import Course


class InMemoryStore:
    def __init__(self):
        self.courses: Dict[str, Course] = {}

    def course(self, course_id: str) -> Optional[Course]:
        return self.courses.get(course_id)
