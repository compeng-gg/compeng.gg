from rest_framework.permissions import IsAuthenticated
import courses.models as db
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone


class StudentCanTakeQuiz(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        user_id = request.user.id

        course_slug = view.kwargs.get("course_slug")

        quiz_slug = view.kwargs.get("quiz_slug")

        try:
            quiz = db.Quiz.objects.get(
                slug=quiz_slug, offering__course__slug=course_slug
            )
            request.quiz = quiz
        except db.Quiz.DoesNotExist:
            raise PermissionDenied("Quiz not found")

        try:
            db.Enrollment.objects.get(
                role__kind=db.Role.Kind.STUDENT,
                role__offering=quiz.offering,
                user_id=user_id,
            )
        except db.Enrollment.DoesNotExist:
            raise PermissionDenied("Student is not enrolled in this course")

        if quiz.starts_at > timezone.now():
            raise PermissionDenied("Quiz has not started yet")

        return True


class StudentCanAnswerQuiz(StudentCanTakeQuiz):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        user_id = request.user.id
        quiz = request.quiz
        try:
            quiz_submission = db.QuizSubmission.objects.get(
                quiz=quiz,
                user_id=user_id,
            )
            request.quiz_submission = quiz_submission
        except db.QuizSubmission.DoesNotExist:
            raise PermissionDenied("Quiz submission not found")

        if timezone.now() > quiz_submission.completed_at:
            raise PermissionDenied("The quiz has already been completed")

        return True
