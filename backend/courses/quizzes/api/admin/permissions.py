from rest_framework.permissions import IsAuthenticated
from courses.quizzes.api.admin.utils import validate_user_is_ta_or_instructor_in_course
import courses.models as db
from rest_framework.exceptions import PermissionDenied


class IsAuthenticatedCourseInstructorOrTA(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        user_id = request.user.id

        course_slug = view.kwargs.get("course_slug")

        try:
            validate_user_is_ta_or_instructor_in_course(user_id, course_slug)
        except Exception:
            raise PermissionDenied("User is not a TA or Instructor in this course")

        quiz_slug = view.kwargs.get("quiz_slug")

        # Return early if the quiz slug is not for a specific quiz
        if quiz_slug is None:
            return True

        try:
            quiz = db.Quiz.objects.get(
                slug=quiz_slug, offering__course__slug=course_slug
            )
            request.quiz = quiz
        except db.Quiz.DoesNotExist:
            return False

        return True
