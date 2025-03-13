from tests.utils import TestCasesWithUserAuth, create_quiz, create_user, create_enrollment, create_quiz_accommodation
from rest_framework import status
import courses.models as db


class ListAccommodationsTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str) -> str:
        return f"/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/accommodations/"

    def test_happy_path(self):
        mock_quiz = create_quiz()
        create_enrollment(self.user.id, mock_quiz.offering, db.Role.Kind.TA)
        
        student_user_1 = create_user("student1")
        student_user_2 = create_user("student2")
        student_user_3 = create_user("student3")

        create_enrollment(student_user_1.id, mock_quiz.offering, db.Role.Kind.STUDENT)
        create_enrollment(student_user_2.id, mock_quiz.offering, db.Role.Kind.STUDENT)
        create_enrollment(student_user_3.id, mock_quiz.offering, db.Role.Kind.STUDENT)

        accommodation_1 = create_quiz_accommodation(student_user_1, mock_quiz)
        accommodation_2 = create_quiz_accommodation(student_user_2, mock_quiz)

        expected_accommodation_1_data = {
            "user_id": student_user_1.id,
            "username": student_user_1.username,
            "visible_at_unix_timestamp": int(accommodation_1.visible_at.timestamp()),
            "starts_at_unix_timestamp": int(accommodation_1.starts_at.timestamp()),
            "ends_at_unix_timestamp": int(accommodation_1.ends_at.timestamp()),
        }

        expected_accommodation_2_data = {
            "user_id": student_user_2.id,
            "username": student_user_2.username,
            "visible_at_unix_timestamp": int(accommodation_2.visible_at.timestamp()),
            "starts_at_unix_timestamp": int(accommodation_2.starts_at.timestamp()),
            "ends_at_unix_timestamp": int(accommodation_2.ends_at.timestamp()),
        }

        user_id_to_expected_accommodation_data = {
            student_user_1.id: expected_accommodation_1_data,
            student_user_2.id: expected_accommodation_2_data,
        }

        response = self.client.get(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        print(response_data)

        self.assertEqual(len(response_data["quiz_accommodations"]), 2)

        for accommodation_data in response_data["quiz_accommodations"]:
            user_id = accommodation_data["user_id"]
            self.assertEqual(accommodation_data, user_id_to_expected_accommodation_data[user_id])
    