from compeng_gg.rest_api import RestAPI

from django.conf import settings

import logging
import json
import jwt
import requests
import time

logger = logging.getLogger(__name__)

class YouTubeRestAPI(RestAPI):

    API_URL = 'https://www.googleapis.com/youtube'

    def __init__(self):
        super().__init__()
