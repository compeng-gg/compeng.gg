from django.core.management.base import BaseCommand
import courses.models as db
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

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
            slug="ece344",
            name="ECE344",
            title="Operating Systems"
        )

        now_datetime = timezone.now()

        mock_offering = db.Offering.objects.create(
            course=mock_course,
            slug="2024-fall",
            name="2024 Fall",
            start=now_datetime,
            end=now_datetime + timedelta(days=365),
            active=True
        )

        mock_student_role = db.Role.objects.create(
            kind=db.Role.Kind.STUDENT,
            offering=mock_offering,
            github_team_slug="2024-fall-ece344-student"
        )

        mock_instructor_role = db.Role.objects.create(
            kind=db.Role.Kind.INSTRUCTOR,
            offering=mock_offering,
            github_team_slug="2024-fall-ece344-instructor"
        )

        mock_ta_role = db.Role.objects.create(
            kind=db.Role.Kind.TA,
            offering=mock_offering,
            github_team_slug="2024-fall-ece344-ta"
        )

        # Superuser 
        User.objects.create_superuser(username="superuser", email="superuser@gmail.com", password="password")

        # Normal student users
        mock_student_user_1 = User.objects.create_user(username="student_1", password="password")
        mock_student_user_2 = User.objects.create_user(username="student_2", password="password")

        mock_instructor_user_1 = User.objects.create_user(username="instructor_1", password="password")

        mock_ta_user_1 = User.objects.create_user(username="ta_1", password="password")

        mock_student_enrollment_1 = db.Enrollment.objects.create(
            user=mock_student_user_1,
            role=mock_student_role
        )
        mock_student_enrollment_2 = db.Enrollment.objects.create(
            user=mock_student_user_2,
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

        mock_content_type = ContentType.objects.create(app_label="your_app", model="mock_model")

        # mock_repository = db.Repository.objects.create(
        #     id=1,
        #     name="reimagined-parakeet",
        #     full_name="nickwood5/reimagined-parakeet",
        #     owner_content_type=mock_content_type,
        #     owner_id=1,
        # )


        # mock_quiz = db.Quiz.objects.create(
        #     slug="quiz-slug",
        #     offering=mock_offering,
        #     title="Quiz Title",
        #     visible_at=now_datetime,
        #     starts_at=now_datetime,
        #     ends_at=now_datetime + timedelta(days=365),
        #     repository=mock_repository
        # )

        # db.CheckboxQuestion.objects.create(
        #     prompt="Answer the checkbox question",
        #     points=20,
        #     order=1,
        #     quiz=mock_quiz,
        #     options=['1', '2', '3'],
        #     correct_option_indices=[0, 1]
        # )

        # db.MultipleChoiceQuestion.objects.create(
        #     prompt="Prompt for a multiple choice question",
        #     points=20,
        #     order=2,
        #     quiz=mock_quiz,
        #     options=['Correct Option', 'Incorrect Option 1', 'Incorrect Option 2'],
        #     correct_option_index=0,
        # )

        # db.CodingQuestion.objects.create(
        #     prompt="Prompt for a C++ coding question",
        #     points=15,
        #     order=3,
        #     quiz=mock_quiz,
        #     starter_code=None,
        #     programming_language=db.CodingQuestion.ProgrammingLanguage.C_PP,
        #     file_to_replace="question1/add.py",
        #     grading_file_directory="question1",
        #     files=["TODO"]
        # )

        # python_coding_question = db.CodingQuestion.objects.create(
        #     prompt="Write a Python function `add(num1, num2)` that adds two integers.",
        #     points=25,
        #     order=4,
        #     quiz=mock_quiz,
        #     starter_code=None,
        #     programming_language=db.CodingQuestion.ProgrammingLanguage.PYTHON,
        #     file_to_replace="question1/add.py",
        #     grading_file_directory="question1",
        #     files=["question1/add.py"]
        # )

        # db.WrittenResponseQuestion.objects.create(
        #     prompt="Prompt for a written response question",
        #     points=25,
        #     order=5,
        #     quiz=mock_quiz,
        #     max_length=200,
        # )

        print("Populated DB with mock data!")