from django.core.management.base import BaseCommand
import courses.models as db
from django.contrib.auth.models import User
from datetime import datetime, timedelta

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

        now_datetime = datetime.now()

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

        db.Exam.objects.create(
            slug="exam-slug",
            offering=mock_offering,
            title="Exam Title",
            visible_at=now_datetime,
            starts_at=now_datetime,
            ends_at=now_datetime + timedelta(days=365)
        )

        print("Populated DB with mock data!")