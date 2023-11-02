from django.conf import settings
from django.test import TestCase
from django.urls import reverse

class AnalyzerTestCase(TestCase):

    def setUp(self):
        pass

    def test_webhook_unauthorized(self):
        response = self.client.post(reverse("analyzer:webhook"))
        self.assertEqual(response.status_code, 401)

    def test_webhook_wrong_token(self):
        response = self.client.post(
            reverse("analyzer:webhook"),
            headers={'X-Gitlab-Token': 'invalid'}
        )
        self.assertEqual(response.status_code, 401)

    def test_webhook(self):
        response = self.client.post(
            reverse("analyzer:webhook"),
            {'username': 'jon'},
            headers={
                'X-Gitlab-Token': settings.ANALYZER_SECRET_TOKEN,
                'Content-Type': 'application/json',
            },
        )
        self.assertEqual(response.status_code, 200)
