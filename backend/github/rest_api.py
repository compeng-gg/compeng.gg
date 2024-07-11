from compeng_gg.rest_api import RestAPI

from django.conf import settings

from cryptography.hazmat.primitives.serialization import load_pem_private_key

import json
import jwt
import requests
import time

class GitHubRestAPI(RestAPI):

    URL = 'https://api.github.com'
    CLIENT_ID = settings.SOCIAL_AUTH_GITHUB_KEY
    CLIENT_SECRET = settings.SOCIAL_AUTH_GITHUB_SECRET
    ORGANIZATION = settings.GITHUB_ORGANIZATION
    PRIVATE_KEY = load_pem_private_key(
        settings.GITHUB_PRIVATE_KEY_PEM.encode(encoding='ascii'), password=None
    )

    def __init__(self):
        self.ghs_token = None

    def generate_jwt_token(self):
        payload = {
            'iat': int(time.time()),
            'exp': int(time.time()) + 600,
            'iss': self.CLIENT_ID,
        }
        return jwt.encode(payload, self.PRIVATE_KEY, algorithm='RS256')

    def generate_ghs_token(self):
        if not self.ghs_token:
            url = self.access_tokens_url()
            data = self.access_tokens(url)
            self.ghs_token = data['token']
        return self.ghs_token

    def app_installations(self):
        token = self.generate_jwt_token()
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
        }
        r = requests.get(
            f'{self.URL}/app/installations',
            headers=headers,
        )
        r.raise_for_status()
        return r.json()

    def access_tokens(self, url):
        token = self.generate_jwt_token()
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
        }
        r = requests.post(
            "https://api.github.com/app/installations/52683225/access_tokens",
            headers=headers,
        )
        r.raise_for_status()
        return r.json()
    
    def access_tokens_url(self):
        installations = self.app_installations()
        for installation in installations:
            if installation['account']['login'] == self.ORGANIZATION:
                return installation['access_tokens_url']
        raise Exception('access_tokens_url not found')

    def list_teams(self):
        token = self.generate_ghs_token()
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
        }
        r = requests.get(
            f'{self.URL}/orgs/{self.ORGANIZATION}/teams',
            headers=headers,
        )
        r.raise_for_status()
        return r.json()

    def create_team(self, name):
        token = self.generate_ghs_token()
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
        }
        data  = {
            "name": name,
            "description": "",
            "permission": "push",
            "notification_setting": "notifications_enabled",
            "privacy": "secret",
        }
        r = requests.post(
            f'{self.URL}/orgs/{self.ORGANIZATION}/teams',
            headers=headers,
            json=data,
        )
        print(r.json())

    def create_repoistory(self, name):
        token = self.generate_ghs_token()
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
        }
        data = {
            "name": name,
            "description": "This is your first repository",
            "homepage": "https://github.com",
            "private": False,
            "has_issues": True,
            "has_projects": True,
            "has_wiki": True,
        }
        r = requests.post(
            f'{self.URL}/orgs/{self.ORGANIZATION}/repos',
            headers=headers,
            json=data,
        )
        # r.raise_for_status()
        print('Response:', json.dumps(r.json(), indent=4))

    def test(self):
        print(self.list_teams())
        self.create_team(name='2024 Fall ECE344 Instructor')
        self.create_team(name='2024 Fall ECE344 TA')
        self.create_team(name='2024 Fall ECE344 Student')
