from django.contrib import admin
from . import models

@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Institution)
class InstitutionAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Offering)
class OfferingAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    pass

@admin.register(models.Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    pass

@admin.register(models.AssignmentTask)
class AssignmentTaskAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    pass

@admin.register(models.TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    pass