from courses.quizzes.api.admin.utils import validate_user_is_ta_or_instructor_in_course
from rest_framework.permissions import IsAuthenticated
import courses.models as db
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone


class StudentCanViewQuiz(IsAuthenticated):
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

        try:
            quiz_submission = db.QuizSubmission.objects.get(quiz=quiz, user_id=user_id)
        except db.QuizSubmission.DoesNotExist:
            quiz_submission = None

        request.quiz_submission = quiz_submission

        try:
            accommodation = db.QuizAccommodation.objects.get(quiz=quiz, user_id=user_id)
        except db.QuizAccommodation.DoesNotExist:
            accommodation = None

        request.accommodation = accommodation

        now = timezone.now()

        quiz_starts_at = (
            quiz.starts_at if accommodation is None else accommodation.starts_at
        )
        quiz_ends_at = quiz.ends_at if accommodation is None else accommodation.ends_at

        is_quiz_submitted = (
            quiz_submission is not None and quiz_submission.completed_at <= now
        )

        # There are 3 cases where a student can view the quiz:

        # 1. The quiz is currently active (between starts_at and ends_at), and they have not submitted it yet.

        if quiz_starts_at <= now <= quiz_ends_at and not is_quiz_submitted:
            return True

        # 2. The quiz content is viewable immediately after submission
        if quiz.content_viewable_after_submission:
            return True

        # 3. Answers/solutions are released after the quiz ends
        if now >= quiz.release_answers_at:
            return True

        # Deny access if none of the above conditions are met
        raise PermissionDenied("Student is not allowed to view this quiz")


class StudentCanAnswerQuiz(StudentCanViewQuiz):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        quiz_submission = request.quiz_submission

        if quiz_submission is None:
            raise PermissionDenied("Quiz submission not found")

        if quiz_submission.completed_at < timezone.now():
            raise PermissionDenied("Quiz has already been completed")

        return True


class StudentCanViewQuizOrInstructor(StudentCanViewQuiz):
    def has_permission(self, request, view):
        user_id = request.user.id

        course_slug = view.kwargs.get("course_slug")

        try:
            validate_user_is_ta_or_instructor_in_course(user_id, course_slug)
            quiz_slug = view.kwargs.get("quiz_slug")

            # Return early if the quiz slug is not for a specific quiz
            if quiz_slug is None:
                return True

            quiz = db.Quiz.objects.get(
                slug=quiz_slug, offering__course__slug=course_slug
            )
            request.quiz = quiz
            return True

        except Exception:
            pass
        return super().has_permission(request, view)
