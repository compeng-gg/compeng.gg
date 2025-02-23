import courses.models as db
from django.db.models import Q


class CustomException(Exception):
    pass


def validate_user_is_ta_or_instructor_in_course(user_id: int, course_slug: str) -> None:
    try:
        db.Enrollment.objects.get(
            (Q(role__kind=db.Role.Kind.TA) | Q(role__kind=db.Role.Kind.INSTRUCTOR)),
            role__offering__course__slug=course_slug,
            user_id=user_id,
        )
    except db.Enrollment.DoesNotExist:
        raise CustomException("User is not a TA or Instructor in this course")
