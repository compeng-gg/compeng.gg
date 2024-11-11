import courses.models as db
from datetime import datetime, timedelta
from django.test import TestCase
import courses.models as db
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def create_offering(offering_name: str="ece496 fall 2024", course_name: str="ece496") -> db.Offering:
    intitution = db.Institution.objects.create()
    course = db.Course.objects.create(
        institution=intitution,
        name=course_name,
        slug="test",
        
    )
    offering = db.Offering.objects.create(
        name=offering_name,
        course=course,
        start=datetime.now(),
        end=datetime.now() + timedelta(days=100),
        active=True
    )

    return offering

def create_offering_teams_settings(offering: db.Offering, max_team_size=3,formation_deadline=datetime.now()+timedelta(days=1)) -> db.OfferingTeamsSettings:
    return db.OfferingTeamsSettings.objects.create(
        offering=offering,
        max_team_size=max_team_size,
        formation_deadline=formation_deadline,
    )


class TestCasesWithUserAuth(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
