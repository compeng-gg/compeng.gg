from django.contrib import admin
from . import models

@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Institution)
class InstitutionAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Semester)
class SemesterAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Offering)
class OfferingAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    pass

@admin.register(models.AssignmentTask)
class AssignmentTaskAdmin(admin.ModelAdmin):
    pass

@admin.register(models.AssignmentResult)
class AssignmentResultAdmin(admin.ModelAdmin):
    pass

@admin.register(models.AssignmentLeaderboardEntry)
class AssignmentLeaderboardEntryAdmin(admin.ModelAdmin):
    pass

@admin.register(models.AssignmentGrade)
class AssignmentGradeAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    pass
