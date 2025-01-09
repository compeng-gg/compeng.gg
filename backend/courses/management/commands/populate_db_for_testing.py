from django.core.management.base import BaseCommand
import courses.models as db
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populates the database with test data'

    def handle(self, *args, **kwargs):
        print("THIS WILL ADD A BUNCH OF TEST DATA TO THE DB")
        print("DON'T RUN THIS IN PROD. IT SHOULD ONLY BE USED FOR LOCAL DEVELOPMENT")

        user_input = input("Continue? [y/n]:")

        if user_input != "y":
            return
        
        
        mock_institution = db.Institution.objects.create(
            slug="institution-slug",
            name="Institution Name"
        )

        mock_course = db.Course.objects.create(
            institution=mock_institution,
            slug="course-slug",
            name="The Course Name",
            title="The Course Title"
        )

        now_datetime = timezone.now()

        mock_offering = db.Offering.objects.create(
            course=mock_course,
            slug="offering-slug",
            name="The Course Offering Name",
            start=now_datetime,
            end=now_datetime + timedelta(days=365),
            active=True
        )

        mock_student_role = db.Role.objects.create(
            kind=db.Role.Kind.STUDENT,
            offering=mock_offering
        )

        mock_instructor_role = db.Role.objects.create(
            kind=db.Role.Kind.INSTRUCTOR,
            offering=mock_offering
        )

        mock_ta_role = db.Role.objects.create(
            kind=db.Role.Kind.TA,
            offering=mock_offering
        )

        # Superuser 
        User.objects.create_superuser(username="superuser", email="superuser@gmail.com", password="password")

        # Normal student users
        mock_student_user_1 = User.objects.create_user(username="student_1", password="password")

        mock_instructor_user_1 = User.objects.create_user(username="instructor_1", password="password")

        mock_ta_user_1 = User.objects.create_user(username="ta_1", password="password")

        mock_student_enrollment_1 = db.Enrollment.objects.create(
            user=mock_student_user_1,
            role=mock_student_role
        )

        mock_instructor_enrollment_1 = db.Enrollment.objects.create(
            user=mock_instructor_user_1,
            role=mock_instructor_role
        )

        mock_ta_enrollment_1 = db.Enrollment.objects.create(
            user=mock_ta_user_1,
            role=mock_ta_role
        )

        mock_quiz = db.Quiz.objects.create(
            slug="quiz-slug",
            offering=mock_offering,
            title="Quiz Title",
            visible_at=now_datetime,
            starts_at=now_datetime,
            ends_at=now_datetime + timedelta(days=365)
        )

        db.CheckboxQuestion.objects.create(
            prompt="Answer the checkbox question",
            points=20,
            order=1,
            quiz=mock_quiz,
            options=['1', '2', '3'],
            correct_option_indices=[0, 1]
        )

        db.MultipleChoiceQuestion.objects.create(
            prompt="Prompt for a multiple choice question",
            points=20,
            order=2,
            quiz=mock_quiz,
            options=['Correct Option', 'Incorrect Option 1', 'Incorrect Option 2'],
            correct_option_index=0,
        )

        db.CodingQuestion.objects.create(
            prompt="Prompt for a C++ coding question",
            points=15,
            order=3,
            quiz=mock_quiz,
            starter_code=None,
            programming_language=db.CodingQuestion.ProgrammingLanguage.C_PP
        )

        db.CodingQuestion.objects.create(
            prompt="Prompt for a Python coding question",
            points=25,
            order=4,
            quiz=mock_quiz,
            starter_code=None,
            programming_language=db.CodingQuestion.ProgrammingLanguage.PYTHON
        )

        db.WrittenResponseQuestion.objects.create(
            prompt="Prompt for a written response question",
            points=25,
            order=5,
            quiz=mock_quiz,
            max_length=200,
        )

        print("Populated DB with mock data!")