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

@admin.register(models.Exam)
class ExamAdmin(admin.ModelAdmin):
    pass

@admin.register(models.WrittenResponseQuestion)
class WrittenResponseQuestionAdmn(admin.ModelAdmin):
    pass

@admin.register(models.CodingQuestion)
class CodingQuestionAdmn(admin.ModelAdmin):
    pass

@admin.register(models.MultipleChoiceQuestion)
class MultipleChoiceQuestionAdmn(admin.ModelAdmin):
    pass

@admin.register(models.CheckboxQuestion)
class CheckboxQuestionAdmin(admin.ModelAdmin):
    pass

@admin.register(models.ExamSubmission)
class ExamSubmissionAdmin(admin.ModelAdmin):
    pass

@admin.register(models.CheckboxAnswer)
class CheckboxAnswerAdmin(admin.ModelAdmin):
    pass

@admin.register(models.MultipleChoiceAnswer)
class MultipleChoiceAdmin(admin.ModelAdmin):
    pass