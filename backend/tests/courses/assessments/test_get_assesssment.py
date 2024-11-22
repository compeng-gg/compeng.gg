from tests.utils import create_offering, TestCasesWithUserAuth
from django.contrib.auth.models import User
import courses.models as db
from datetime import (
    datetime,
    timedelta,
)


class GetAssessmentTests(TestCasesWithUserAuth):
    def test_creates_new_submission_on_first_request_happy_path(self):


        offering = create_offering()
        
        student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)
        
        requesting_user = self.user

        enrollment = db.Enrollment.objects.create(
            user=requesting_user,
            role=student_role,
        )

        print(f"Create enrol for {requesting_user.id}")

        start_datetime = datetime.now()
        end_datetime = start_datetime + timedelta(hours=1)

        assessment = db.Assessment.objects.create(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            offering=offering,
        )

        db.CodingQuestion.objects.create(
            assessment=assessment,
            prompt="Explain this",
            order=1,
        )

        db.MultipleChoiceQuestion.objects.create(
            assessment=assessment,
            prompt="Explain this",
            order=1,
            options=[
                "test"
            ],
            correct_option_index=0
        )

        db.WrittenResponseQuestion.objects.create(
            assessment=assessment,
            prompt="Explain this",
            order=1,
        )

        self.client.force_login(requesting_user)
        print(f"Test client logged in user: {self.client.session.get('_auth_user_id')}")

        # Initially no submission should exist
        self.assertFalse(db.AssessmentSubmission.objects.filter(
            enrollment=enrollment,
            assessment=assessment
        ).exists())

        response = self.client.get(
            f"/api/v0/assessments/{assessment.id}/",
        )
        print(response.json())
        self.assertEqual(
            response.status_code, 200
        )

        self.assertTrue(db.AssessmentSubmission.objects.filter(
            enrollment=enrollment,
            assessment=assessment
        ).exists())

        print('dd')
        print(response.json())

        exit()