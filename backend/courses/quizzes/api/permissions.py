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

        if accommodation:
            if accommodation.starts_at > now:
                raise PermissionDenied("Accommodation has not started yet")
            if accommodation.ends_at < now:
                raise PermissionDenied("Accommodation has already ended")
            return True

        if quiz.starts_at <= now <= quiz.ends_at:
            return True

        if quiz.content_viewable_after_submission and now >= quiz.visible_at:
            return True

        if now >= quiz.release_answers_at:
            return True

        raise PermissionDenied("You do not have access to view this quiz at this time.")


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

        except:
            pass
        return super().has_permission(request, view)
