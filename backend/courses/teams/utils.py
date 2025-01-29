from rest_framework import permissions
from courses.models import Role, Enrollment
class IsInstructorOrTA(permissions.BasePermission):
    def has_permission(self, request, view):
        has_permission = Enrollment.objects.filter(
            user=request.user,
            role__kind__in=[Role.Kind.INSTRUCTOR, Role.Kind.TA]
        ).exists()
        print(f"Permission check for user {request.user}: {has_permission}")
        return has_permission