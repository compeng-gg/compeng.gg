from rest_framework import permissions
from courses.models import Role
class IsInstructorOrTA(permissions.BasePermission):
    def has_permission(self, request, view):
        # Assuming the user's role is associated with an `Enrollment` or similar model
        return Role.objects.filter(
            user=request.user,
            kind__in=[Role.Kind.INSTRUCTOR, Role.Kind.TA]
        ).exists()