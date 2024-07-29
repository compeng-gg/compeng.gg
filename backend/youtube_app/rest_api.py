from django.conf import settings

from compeng_gg.auth import get_access_token
from compeng_gg.rest_api import RestAPI

import logging
import json
import requests

logger = logging.getLogger(__name__)

class YouTubeRestAPI(RestAPI):

    API_URL = 'https://www.googleapis.com/youtube/v3'

    def __init__(self, user):
        super().__init__()
        self.access_token = get_access_token('google', user)

    def get(self, endpoint):
        token = self.access_token
        headers = {
            'Authorization': f'Bearer {token}',
        }
        r = requests.get(
            f'{self.API_URL}{endpoint}',
            headers=headers,
        )
        r.raise_for_status()
        if r.text == '':
            return None
        return r.json()

    def list_channels(self):
        return self.get('/channels?mine=true&part=snippet,contentDetails')

    def test(self):
        print(json.dumps(self.list_channels(), indent=4))
