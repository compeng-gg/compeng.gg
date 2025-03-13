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

@admin.register(models.OfferingTeamsSettings)
class OfferingTeamsSettingsAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    pass

@admin.register(models.TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
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

@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
    pass

@admin.register(models.TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'team')
    list_display_links = ('enrollment', 'team')
    
    pass

@admin.register(models.OfferingTeamsSettings)
class OfferingTeamsSettingsAdmin(admin.ModelAdmin):
    list_display = ('offering', 'max_team_size', 'formation_deadline')
    list_display_links = ('offering', 'max_team_size', 'formation_deadline')

@admin.register(models.Assessment)
class AssessmentAdmin(admin.ModelAdmin):
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

@admin.register(models.QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    pass

@admin.register(models.CheckboxAnswer)
class CheckboxAnswerAdmin(admin.ModelAdmin):
    pass

@admin.register(models.MultipleChoiceAnswer)
class MultipleChoiceAdmin(admin.ModelAdmin):
    pass

@admin.register(models.CodingAnswer)
class CodingAnswerAdmin(admin.ModelAdmin):
    pass

@admin.register(models.CodingAnswerExecution)
class CodingAnswerExecutionAdmin(admin.ModelAdmin):
    pass

@admin.register(models.QuestionImage)
class QuestionImageAdmin(admin.ModelAdmin):
    pass