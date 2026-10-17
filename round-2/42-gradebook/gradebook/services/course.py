from datetime import datetime
from decimal import Decimal, InvalidOperation

from ..config import WEIGHTS
from ..errors import GradebookError, NotFound
from ..models import Assignment, Course, Submission
from ..store import InMemoryStore
from .grading import course_percent, letter


class CourseService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def create(self, course_id: str, students) -> Course:
        course = Course(course_id, students=set(students))
        self._store.courses[course_id] = course
        return course

    def _course(self, course_id: str) -> Course:
        course = self._store.course(course_id)
        if course is None:
            raise NotFound(course_id)
        return course

    def add_assignment(self, course_id: str, assignment_id: str, category: str, max_points, due: datetime) -> Assignment:
        if category not in WEIGHTS:
            raise GradebookError(f"unknown category {category}")
        a = Assignment(assignment_id, category, Decimal(str(max_points)), due)
        self._course(course_id).assignments[assignment_id] = a
        return a

    def submit(self, course_id: str, student: str, assignment_id: str, at: datetime) -> Submission:
        course = self._course(course_id)
        if student not in course.students or assignment_id not in course.assignments:
            raise NotFound("unknown student or assignment")
        sub = Submission(student, assignment_id, at)
        course.submissions[(student, assignment_id)] = sub
        return sub

    def grade(self, course_id: str, student: str, assignment_id: str, points) -> Submission:
        course = self._course(course_id)
        sub = course.submissions.get((student, assignment_id))
        if sub is None:
            raise NotFound("no submission to grade")
        try:
            points = Decimal(str(points))
        except InvalidOperation:
            raise GradebookError("points must be a number")
        if not 0 <= points <= course.assignments[assignment_id].max_points:
            raise GradebookError("points out of range")
        sub.points = points
        return sub

    def excuse(self, course_id: str, student: str, assignment_id: str) -> None:
        self._course(course_id).excused.add((student, assignment_id))

    def report(self, course_id: str, student: str) -> dict:
        course = self._course(course_id)
        pct = course_percent(course, student)
        return {"student": student, "percent": str(pct.quantize(Decimal("0.01"))), "letter": letter(pct)}
