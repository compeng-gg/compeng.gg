import requests

from urllib.parse import urlencode

class GitHubApi:

    URL = "https://api.github.com"

    def __init__(self):
        pass

    def _request(self, endpoint, query_params=None, method="GET"):
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if query_params:
            endpoint = f"{endpoint}?{urlencode(query_params)}"
        request = getattr(requests, method.lower())
        response = request(f"{self.URL}{endpoint}", headers=headers)
        return response.json()

    def get_commit(self, owner, repo, ref):
        return self._request(f"/repos/{owner}/{repo}/commits/{ref}")

    def list_commits(self, owner, repo, sha=None, per_page=None):
        query_params = {}
        if sha:
            query_params["sha"] = sha
        if per_page:
            query_params["per_page"] = per_page
        return self._request(
            f"/repos/{owner}/{repo}/commits",
            query_params=query_params
        )

    def list_organization_repositories(self, org):
        return self._request(f"/orgs/{org}/repos")
