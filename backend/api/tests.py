from django.test import TestCase

from rest_framework import status

class TestMyModelLogAPIs(TestCase):

    def test_get_all_my_model(self):
        response = self.client.get('/api/v0/users/self/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
