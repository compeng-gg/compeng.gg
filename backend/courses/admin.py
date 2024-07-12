from django.contrib import admin
from .models import (
    Course,
    Institution,
    Offering,
    Role,
    Enrollment,
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    pass

@admin.register(Offering)
class OfferingAdmin(admin.ModelAdmin):
    pass

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    pass
