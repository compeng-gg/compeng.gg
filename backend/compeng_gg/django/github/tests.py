import hashlib
import hmac
import json

from compeng_gg.django.github.rest_framework import views as rest_views
from compeng_gg.django.github.models import (
    Commit,
    Delivery,
    Hook,
    Organization,
    Path,
    Push,
    Repository,
    Team,
    User,
)
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory
from uuid import uuid4

class GitHubTestCase(TestCase):

    def setUp(self):
        hook_id = 1
        response, delivery_uuid = self._delivery("ping", {
            "hook_id": hook_id,
            "hook": {
                "id": 1,
                "type": "Organization",
            },
            "organization": self._organization_data(1, "ece-gg"),
            "sender": self._user_data(2, "eyolfson"),
        }, hook_id=hook_id)
        hook = Hook.objects.get(id=hook_id)
        self.assertTrue(isinstance(hook.installation_target, Organization))

    def _user_data(self, pk, username):
        return {
            "id": pk,
            "login": username,
            "type": "User",
            "site_admin": False,
            "gravatar_id": "",
            "user_view_type": "public",
        }
    
    def _org_user_data(self, pk, username):
        return {
            "id": pk,
            "login": username,
            "type": "Organization",
            "site_admin": False,
            "gravatar_id": "",
            "user_view_type": "public",
        }

    def _organization_data(self, pk, username):
        return {
            "id": pk,
            "login": username,
            "description": "",
        }

    def _repository_data(self, pk, name, full_name, owner_data):
        return {
            "id": pk,
            "fork": False,
            "name": name,
            "size": 0,
            "forks": 0,
            "owner": owner_data,
            "topics": [],
            "git_url": "",
            "license": {},
            "private": True,
            "ssh_url": "",
            "svn_url": "",
            "archived": False,
            "disabled": False,
            "has_wiki": True,
            "homepage": None,
            "html_url": "",
            "language": "",
            "watchers": 0,
            "clone_url": "",
            "full_name": full_name,
            "has_pages": False,
            "pushed_at": "",
            "created_at": "",
            "has_issues": True,
            "mirror_url": None,
            "updated_at": "",
            "visibility": "private",
            "description": None,
            "forks_count": 0,
            "is_template": False,
            "open_issues": 0,
            "has_projects": True,
            "allow_forking": False,
            "has_downloads": True,
            "default_branch": "main",
            "watchers_count": 0,
            "has_discussions": False,
            "stargazers_count": 0,
            "custom_properties": {},
            "open_issues_count": 0,
            "web_commit_signoff_required": False,
        }

    def _commit_data(self, sha1, message="", added=[], modified=[], removed=[]):
        return {
            "id": sha1,
            "added": added,
            "message": message,
            "removed": removed,
            "tree_id": "",
            "distinct": True,
            "modified": modified,
            "timestamp": "",
        }

    def _team_data(self, pk, slug, name):
        return {
            "id": pk,
            "name": name,
            "slug": slug,
            "parent": None,
            "privacy": "closed",
            "permission": "pull",
            "description": "",
            "notification_setting": "notifications_enabled"
        }

    def _delivery(self, event, payload, hook_id=1):
        delivery_uuid = str(uuid4())
        data = json.dumps(payload).encode()

        secret = settings.GITHUB_WEBHOOK_SECRET.encode()
        digest_maker = hmac.new(secret, data, digestmod=hashlib.sha256)
        digest = digest_maker.hexdigest()

        factory = APIRequestFactory()
        request = factory.post("/api/github/webhook/", data,
            content_type='application/json',
            headers={
                "X-GitHub-Delivery": delivery_uuid,
                "X-GitHub-Event": event,
                "X-Hub-Signature-256": f"sha256={digest}",
                "X-GitHub-Hook-ID": hook_id,
            },
        )
        response = rest_views.webhook(request)
        return response, delivery_uuid

    def test_push(self):
        commit_data = self._commit_data(
            "0123456789abcedf0123456789abcdef01234567",
            modified=["README.md"],
        )
        response, delivery_uuid = self._delivery("push", {
            "ref": "refs/heads/main",
            "repository": self._repository_data(
                1,
                "test",
                "ece-gg/test",
                self._org_user_data(1, "ece-gg")
            ),
            "commits": [
                commit_data,
            ],
            "head_commit": commit_data,
            "sender": self._user_data(2, "eyolfson"),
        })
        self.assertEqual(response.status_code, 200)

        content_type = ContentType.objects.get_for_model(Push)
        delivery = Delivery.objects.get(uuid=delivery_uuid)
        self.assertEqual(delivery.event, "push")
        self.assertEqual(delivery.content_type, content_type)

        organization = Organization.objects.get(id=1)
        self.assertEqual(organization.login, "ece-gg")

        user = User.objects.get(id=2)
        self.assertEqual(user.login, "eyolfson")

        repository = Repository.objects.get(id=1)
        self.assertEqual(repository.name, "test")
        self.assertEqual(repository.full_name, "ece-gg/test")
        self.assertEqual(repository.owner, organization)

        commit = Commit.objects.get(
            repository=repository,
            sha1="0123456789abcedf0123456789abcdef01234567",
        )
    
        push = delivery.content_object
        self.assertEqual(push.head_commit, commit)
        self.assertEqual(push.ref, "refs/heads/main")
        self.assertEqual(push.sender, user)
        self.assertEqual(push.repository, repository)

        self.assertEqual(repository, organization.owned_repositories.get())
        self.assertEqual(commit, repository.commits.get())
        self.assertEqual(push, commit.pushes_head.get())
        self.assertEqual(push, repository.pushes.get())
        self.assertEqual(push, user.pushes.get())

        self.assertEqual(delivery, push.delivery)
        self.assertEqual(push, delivery.push)

        self.assertEqual(commit.pushes.count(), 1)
        self.assertEqual(push.commits.count(), 1)

        path = Path.objects.get(
            repository=repository,
            relative="README.md",
        )
        self.assertEqual(path, commit.paths_modified.get())

    def test_team_created(self):
        response, delivery_uuid = self._delivery("team", {
            "action": "created",
            "team": self._team_data(1, "team-1", "Team 1"),
            "organization": self._organization_data(1, "ece-gg"),
            "sender": self._user_data(2, "eyolfson"),
        })
        self.assertEqual(response.status_code, 200)

        team = Team.objects.get(id=1)
        self.assertEqual(team.slug, "team-1")
        self.assertEqual(team.name, "Team 1")
        self.assertEqual(team.members.count(), 1)

    def test_team_edited(self):
        organization = Organization.objects.get(id=1)
        team = Team.objects.create(
            id=1,
            organization=organization,
            slug="team-1",
            name="Team 1",
        )

        response, delivery_uuid = self._delivery("team", {
            "team": self._team_data(1, "team-2", "Team 2"),
            "action": "edited",
            "sender": self._user_data(2, "eyolfson"),
            "changes": {
                "name": {
                    "from": "Team 1"
                }
            },
            "organization": self._organization_data(1, "ece-gg"),
        })
        self.assertEqual(response.status_code, 200)

        team = Team.objects.get(id=1)
        self.assertEqual(team.slug, "team-2")
        self.assertEqual(team.name, "Team 2")

    def test_membership_team_added(self):
        response, delivery_uuid = self._delivery("membership", {
            "team": self._team_data(1, "team-2", "Team 2"),
            "scope": "team",
            "action": "added",
            "member": self._user_data(3, "jon"),
            "sender": self._user_data(2, "eyolfson"),
            "organization": self._organization_data(1, "ece-gg"),
        })
        self.assertEqual(response.status_code, 200)

        team = Team.objects.get(id=1)
        member = User.objects.get(id=3)
        self.assertEqual(team.members.count(), 1)
        self.assertEqual(team.members.get(), member)

    def test_team(self):
        response, d1_uuid = self._delivery("team", {
            "action": "deleted",
            "team": self._team_data(1, "team-1", "Team 1"),
            "organization": self._organization_data(1, "ece-gg"),
            "sender": self._user_data(2, "eyolfson"), 
        })
        self.assertEqual(response.status_code, 200)

        response, d2_uuid = self._delivery("membership", {
            "action": "removed",
            "scope": "organization",
            "member": self._user_data(3, "user"),
            "team": {
                "id": 1,
                "name": "Team 1",
                "deleted": True,
            },
            "organization": self._organization_data(1, "ece-gg"),
            "sender": self._user_data(2, "eyolfson"), 
        })
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Delivery.objects.count(), 3)
        self.assertEqual(Team.objects.count(), 0)
        self.assertEqual(Organization.objects.count(), 1)
        organization = Organization.objects.get()
        self.assertEqual(organization.id, 1)
        self.assertEqual(organization.login, "ece-gg")
