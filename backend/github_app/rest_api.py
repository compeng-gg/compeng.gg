from compeng_gg.rest_api import RestAPI

from django.conf import settings

from cryptography.hazmat.primitives.serialization import load_pem_private_key

import logging
import json
import jwt
import requests
import time

logger = logging.getLogger(__name__)

class GitHubRestAPI(RestAPI):

    API_URL = 'https://api.github.com'
    CLIENT_ID = settings.SOCIAL_AUTH_GITHUB_KEY
    CLIENT_SECRET = settings.SOCIAL_AUTH_GITHUB_SECRET
    ORGANIZATION = settings.GITHUB_ORGANIZATION
    try:
        PRIVATE_KEY = load_pem_private_key(
            settings.GITHUB_PRIVATE_KEY_PEM.encode(encoding='ascii'), password=None
        )
    except ValueError:
        PRIVATE_KEY = None

    def __init__(self):
        super().__init__()
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
            installation_id = self.get_installation_id_for_org()
            data = self.access_tokens(installation_id)
            self.ghs_token = data['token']
        return self.ghs_token

    def get_with_jwt(self, endpoint):
        token = self.generate_jwt_token()
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
        }
        r = requests.get(
            f'{self.API_URL}{endpoint}',
            headers=headers,
        )
        r.raise_for_status()
        return r.json()

    def get_with_ghs(self, endpoint):
        token = self.generate_ghs_token()
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
        }
        r = requests.get(
            f'{self.API_URL}{endpoint}',
            headers=headers,
        )
        r.raise_for_status()
        return r.json()

    def post_with_jwt(self, endpoint, data=None):
        token = self.generate_jwt_token()
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
        }
        if data is not None:
            r = requests.post(
                f'{self.API_URL}{endpoint}',
                headers=headers,
                json=data,
            )
        else:
            r = requests.post(
                f'{self.API_URL}{endpoint}',
                headers=headers,
            )
        r.raise_for_status()
        return r.json()

    def post_with_ghs(self, endpoint, data=None):
        token = self.generate_ghs_token()
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
        }
        if data is not None:
            r = requests.post(
                f'{self.API_URL}{endpoint}',
                headers=headers,
                json=data,
            )
        else:
            r = requests.post(
                f'{self.API_URL}{endpoint}',
                headers=headers,
            )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f'{err.response.url}: {err.response.text}')
            return None
        return r.json()

    def app_installations(self):
        return self.get_with_jwt('/app/installations')

    def access_tokens(self, installation_id):
        return self.post_with_jwt(
            f'/app/installations/{installation_id}/access_tokens'
        )

    def list_teams(self, org):
        return self.get_with_ghs(f'/orgs/{org}/teams')

    def list_teams_for_org(self):
        return self.list_teams(self.ORGANIZATION)

    def get_team(self, org, team_slug):
        return self.get_with_ghs(f'/orgs/{org}/teams/{team_slug}')

    def get_team_for_org(self, team_slug):
        return self.get_team(self.ORGANIZATION, team_slug)

    def get_installation_id_for_org(self):
        installations = self.app_installations()
        for installation in installations:
            if installation['account']['login'] == self.ORGANIZATION:
                return installation['id']
        raise Exception(f'Installation not found for {self.ORGANIZATION}')

    def create_team(self, org, name):
        data  = {
            "name": name,
            "description": "",
            "permission": "push",
            "notification_setting": "notifications_enabled",
            "privacy": "secret",
        }
        return self.post_with_ghs(f'/orgs/{org}/teams', data)

    def create_team_for_org(self, name):
        return self.create_team(self.ORGANIZATION, name)

    def create_org_repo(self, org, name):
        data = {
            "name": name,
            "description": "This is your first repository",
            "homepage": "https://github.com",
            "private": False,
            "has_issues": True,
            "has_projects": True,
            "has_wiki": False,
        }
        return self.post_with_ghs(f'/orgs/{org}/repos', data)

    def create_org_repo_for_org(self, name):
        return self.create_org_repo(self.ORGANIZATION, name)

    def test(self):
        print(json.dumps(self.list_teams_for_org(), indent=4))
        self.create_team_for_org('2024 Fall ECE344 Instructor')
        self.create_team_for_org('2024 Fall ECE344 TA')
        self.create_team_for_org('2024 Fall ECE344 Student')
