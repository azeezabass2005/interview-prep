from datetime import datetime

from .errors import GradebookError
from .services.course import CourseService


class GradebookApi:
    def __init__(self, service: CourseService):
        self._s = service

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except GradebookError as exc:
            return exc.status, {"error": str(exc)}

    def create(self, course_id: str, students):
        return self._call(lambda: {"course_id": self._s.create(course_id, students).course_id}, 201)

    def assignment(self, course_id: str, body: dict):
        return self._call(lambda: {"id": self._s.add_assignment(course_id, body["id"], body["category"], body["max_points"],
                                                                datetime.fromisoformat(body["due"])).assignment_id}, 201)

    def submit(self, course_id: str, student: str, assignment_id: str, at: str):
        return self._call(lambda: {"ok": bool(self._s.submit(course_id, student, assignment_id, datetime.fromisoformat(at)))}, 201)

    def grade(self, course_id: str, student: str, assignment_id: str, points):
        return self._call(lambda: {"points": str(self._s.grade(course_id, student, assignment_id, points).points)})

    def excuse(self, course_id: str, student: str, assignment_id: str):
        return self._call(lambda: self._s.excuse(course_id, student, assignment_id) or {"excused": True})

    def report(self, course_id: str, student: str):
        return self._call(lambda: self._s.report(course_id, student))
