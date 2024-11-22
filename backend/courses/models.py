from django.conf import settings
from uuid import uuid4
from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

from runner.models import Runner, Task


class Institution(models.Model):

    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=50)
    verified_discord_role_id = models.BigIntegerField(blank=True, null=True)
    first_year_discord_role_id = models.BigIntegerField(blank=True, null=True)
    second_year_discord_role_id = models.BigIntegerField(blank=True, null=True)
    third_year_discord_role_id = models.BigIntegerField(blank=True, null=True)
    fourth_year_discord_role_id = models.BigIntegerField(blank=True, null=True)
    grad_student_discord_role_id = models.BigIntegerField(blank=True, null=True)
    faculty_discord_role_id = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if Offering.objects.filter(course__institution=self,
                                   active=False) \
                           .exists():
            return reverse('courses:archive_institution',
                            kwargs={'institution_slug': self.slug})
        raise NoReverseMatch(f'{self} has no archived offerings')

    class Meta:
        ordering = ['slug']

class Course(models.Model):

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=80)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if Offering.objects.filter(course=self, active=False).exists():
            return reverse('courses:archive_course', kwargs={
                'institution_slug': self.institution.slug,
                'course_slug': self.slug,
            })
        raise NoReverseMatch(f'{self} has no archived offerings')

    class Meta:
        ordering = ['slug']

class Offering(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=50)
    start = models.DateField()
    end = models.DateField()
    active = models.BooleanField()
    external_id = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.name} {self.course}'

    def full_slug(self):
        return f'{self.slug}-{self.course.slug}'

    def get_absolute_url(self):
        if self.active:
            return reverse('courses:course', kwargs={'course_slug': self.course.slug})
        else:
            return reverse('courses:archive_offering', kwargs={
                'institution_slug': self.course.institution.slug,
                'course_slug': self.course.slug,
                'offering_slug': self.slug,
            })

    class Meta:
        ordering = ['-start', 'slug']

class OfferingTeamsSettings(models.Model):
    offering = models.OneToOneField(
        Offering,
        on_delete=models.CASCADE,
    )
    max_team_size = models.IntegerField(default=3)
    formation_deadline = models.DateTimeField(default=(timezone.now))
    show_group_members = models.BooleanField(default=True)
    allow_custom_names = models.BooleanField(default=False)

class Assignment(models.Model):

    offering = models.ForeignKey(
        Offering,
        on_delete=models.CASCADE,
    )
    runner = models.ForeignKey(
        Runner,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=50)
    due_date = models.DateTimeField()
    files = models.JSONField()

    def __str__(self):
        return f'{self.offering} - {self.name}'

    class Meta:
        ordering = ['-due_date']

class Role(models.Model):

    class Kind(models.IntegerChoices):
        INSTRUCTOR = 1, _('Instructor')
        TA = 2, _('TA')
        STUDENT = 3, _('Student')
        AUDIT = 4, _('Audit')

    kind = models.IntegerField(choices=Kind)
    offering = models.ForeignKey(
        Offering,
        on_delete=models.CASCADE,
    )
    discord_role_id = models.BigIntegerField(blank=True, null=True)
    github_team_slug = models.CharField(max_length=128, blank=True, null=False)

    def __str__(self):
        return f'{self.offering} {self.get_kind_display()}'

    class Meta:
        unique_together = ['kind', 'offering']

class Member(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
    )
    external_id = models.BigIntegerField()

    def __str__(self):
        return f'{self.user} ({self.external_id})'

    class Meta:
        unique_together = ['institution', 'external_id']



class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.user} - {self.role}'

    class Meta:
        unique_together = ['user', 'role']


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(default=timezone.now)
    offering = models.ForeignKey(Offering, on_delete=models.CASCADE, related_name='teams')
    github_team_slug = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'offering'], name='unique_team_name_per_offering')
        ]

class TeamMember(models.Model):
    class MembershipType(models.TextChoices):
        MEMBER = "MEMBER", _("Member")
        LEADER = "LEADER", _("Leader")
        REQUESTED_TO_JOIN = "REQUESTED_TO_JOIN", _("Requested to Join")

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    membership_type = models.CharField(
        choices=MembershipType.choices,
        max_length=max(len(choice.value) for choice in MembershipType),
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')


class AssignmentTask(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.user} - {self.assignment} - {self.task}'

class Accommodation(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
    )
    due_date = models.DateTimeField()
    max_grade = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.user} - {self.assignment} - {self.due_date}'

    class Meta:
        unique_together = ['user', 'assignment']


class Assessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    offering = models.ForeignKey(Offering, on_delete=models.CASCADE, related_name='assessments')
    title = models.TextField()

    start_datetime = models.DateTimeField() # TODO: validate end_datetime > start_datetime
    end_datetime = models.DateTimeField()
    

class AssessmentSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="assessment_submissions")
    start_datetime = models.DateTimeField()
    

class AssessmentQuestionBaseModel(models.Model):
    prompt = models.TextField()
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField()

    class Meta:
        abstract = True


class WrittenResponseQuestion(AssessmentQuestionBaseModel):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="written_response_questions")
    max_length = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['assessment', 'order'], name='unique_order_written_response_question'
            )
        ]
    

class WrittenResponseQuestionAnswer(models.Model):
    assessment_submission = models.ForeignKey(AssessmentSubmission, on_delete=models.CASCADE, related_name="written_response_answers")
    question = models.ForeignKey(WrittenResponseQuestion, on_delete=models.CASCADE, related_name="answers")
    
    response = models.TextField()


class CodingQuestion(AssessmentQuestionBaseModel):
    class ProgrammingLanguage(models.TextChoices):
        C_PP = "C_PP", _("C++")
        C = "C", _("C")
        PYTHON = "PYTHON", _("Python")

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="coding_questions")

    starter_code = models.TextField(blank=True, null=True)
    programming_language = models.CharField(
        choices=ProgrammingLanguage.choices,
        max_length=max(len(choice.value) for choice in ProgrammingLanguage),
        blank=False,
        null=False,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['assessment', 'order'], name='unique_order_coding_question'
            )
        ]


class CodingQuestionAnswer(models.Model):
    assessment_submission = models.ForeignKey(AssessmentSubmission, on_delete=models.CASCADE, related_name="coding_question_answers")
    question = models.ForeignKey(CodingQuestion, on_delete=models.CASCADE, related_name="answers")
    
    solution = models.TextField()


class MultipleChoiceQuestion(AssessmentQuestionBaseModel):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="multiple_choice_questions")

    options = models.JSONField() # TODO: validate this is an array
    correct_option_index = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['assessment', 'order'], name='unique_order_multiple_choice_question'
            )
        ]


class MultipleChoiceQuestionAnswer(models.Model):
    assessment_submission = models.ForeignKey(AssessmentSubmission, on_delete=models.CASCADE, related_name="multiple_choice_answers")
    question = models.ForeignKey(MultipleChoiceQuestion, on_delete=models.CASCADE, related_name="answers")
    selected_answer_index = models.PositiveIntegerField()


class CheckboxQuestion(AssessmentQuestionBaseModel):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="checkbox_questions")

    options = models.JSONField() # TODO: validate this is an array
    correct_option_indices = models.JSONField() # TODO: validate this is an array

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['assessment', 'order'], name='unique_order_checkbox_question'
            )
        ]


class CheckboxQuestionAnswer(models.Model):
    assessment_submission = models.ForeignKey(AssessmentSubmission, on_delete=models.CASCADE, related_name="checkbox_answers")
    question = models.ForeignKey(CheckboxQuestion, on_delete=models.CASCADE, related_name="answers")
    
    selected_answer_indices = models.JSONField() # TODO: validate this is an array
