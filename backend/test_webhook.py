import requests

from compeng_gg import settings

def test_webhook():
    headers = {
        'X-GitHub-Event': 'push',
        'X-Hub-Signature-256': 'sha256=aa1747ec22a3a949935a0ceb723d7d115ffe7d64d32abf9792a7ad3687ac8903',
    }
    data = {
        "ref": "refs/heads/main",
        "before": "31e989443fc93f1f98fbe7a40b04eb2d2648b417",
        "after": "742ad44f682ed0bd12eefb9eba72032227a87b12",
        "repository": {
            "id": 850791657,
            "node_id": "R_kgDOMrYM6Q",
            "name": "2024-fall-ece344-eyolfso3",
            "full_name": "compeng-gg-dev/2024-fall-ece344-eyolfso3",
            "private": True,
            "owner": {
            "name": "compeng-gg-dev",
            "email": None,
            "login": "compeng-gg-dev",
            "id": 174743446,
            "node_id": "O_kgDOCmpflg",
            "avatar_url": "https://avatars.githubusercontent.com/u/174743446?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/compeng-gg-dev",
            "html_url": "https://github.com/compeng-gg-dev",
            "followers_url": "https://api.github.com/users/compeng-gg-dev/followers",
            "following_url": "https://api.github.com/users/compeng-gg-dev/following{/other_user}",
            "gists_url": "https://api.github.com/users/compeng-gg-dev/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/compeng-gg-dev/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/compeng-gg-dev/subscriptions",
            "organizations_url": "https://api.github.com/users/compeng-gg-dev/orgs",
            "repos_url": "https://api.github.com/users/compeng-gg-dev/repos",
            "events_url": "https://api.github.com/users/compeng-gg-dev/events{/privacy}",
            "received_events_url": "https://api.github.com/users/compeng-gg-dev/received_events",
            "type": "Organization",
            "site_admin": False
            },
            "html_url": "https://github.com/compeng-gg-dev/2024-fall-ece344-eyolfso3",
            "description": None,
            "fork": True,
            "url": "https://github.com/compeng-gg-dev/2024-fall-ece344-eyolfso3",
            "forks_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/forks",
            "keys_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/collaborators{/collaborator}",
            "teams_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/teams",
            "hooks_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/hooks",
            "issue_events_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/issues/events{/number}",
            "events_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/events",
            "assignees_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/assignees{/user}",
            "branches_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/branches{/branch}",
            "tags_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/tags",
            "blobs_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/git/blobs{/sha}",
            "git_tags_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/git/tags{/sha}",
            "git_refs_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/git/refs{/sha}",
            "trees_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/git/trees{/sha}",
            "statuses_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/statuses/{sha}",
            "languages_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/languages",
            "stargazers_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/stargazers",
            "contributors_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/contributors",
            "subscribers_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/subscribers",
            "subscription_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/subscription",
            "commits_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/commits{/sha}",
            "git_commits_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/git/commits{/sha}",
            "comments_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/comments{/number}",
            "issue_comment_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/issues/comments{/number}",
            "contents_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/contents/{+path}",
            "compare_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/compare/{base}...{head}",
            "merges_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/merges",
            "archive_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/{archive_format}{/ref}",
            "downloads_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/downloads",
            "issues_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/issues{/number}",
            "pulls_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/pulls{/number}",
            "milestones_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/notifications{?since,all,participating}",
            "labels_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/labels{/name}",
            "releases_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/releases{/id}",
            "deployments_url": "https://api.github.com/repos/compeng-gg-dev/2024-fall-ece344-eyolfso3/deployments",
            "created_at": 1725219356,
            "updated_at": "2024-09-01T19:35:56Z",
            "pushed_at": 1725219539,
            "git_url": "git://github.com/compeng-gg-dev/2024-fall-ece344-eyolfso3.git",
            "ssh_url": "git@github.com:compeng-gg-dev/2024-fall-ece344-eyolfso3.git",
            "clone_url": "https://github.com/compeng-gg-dev/2024-fall-ece344-eyolfso3.git",
            "svn_url": "https://github.com/compeng-gg-dev/2024-fall-ece344-eyolfso3",
            "homepage": None,
            "size": 4,
            "stargazers_count": 0,
            "watchers_count": 0,
            "language": None,
            "has_issues": False,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": True,
            "has_pages": False,
            "has_discussions": False,
            "forks_count": 0,
            "mirror_url": None,
            "archived": False,
            "disabled": False,
            "open_issues_count": 0,
            "license": None,
            "allow_forking": True,
            "is_template": False,
            "web_commit_signoff_required": False,
            "topics": [

            ],
            "visibility": "private",
            "forks": 0,
            "open_issues": 0,
            "watchers": 0,
            "default_branch": "main",
            "stargazers": 0,
            "master_branch": "main",
            "organization": "compeng-gg-dev",
            "custom_properties": {

            }
        },
        "pusher": {
            "name": "eyolfson",
            "email": "jon@eyolfson.com"
        },
        "organization": {
            "login": "compeng-gg-dev",
            "id": 174743446,
            "node_id": "O_kgDOCmpflg",
            "url": "https://api.github.com/orgs/compeng-gg-dev",
            "repos_url": "https://api.github.com/orgs/compeng-gg-dev/repos",
            "events_url": "https://api.github.com/orgs/compeng-gg-dev/events",
            "hooks_url": "https://api.github.com/orgs/compeng-gg-dev/hooks",
            "issues_url": "https://api.github.com/orgs/compeng-gg-dev/issues",
            "members_url": "https://api.github.com/orgs/compeng-gg-dev/members{/member}",
            "public_members_url": "https://api.github.com/orgs/compeng-gg-dev/public_members{/member}",
            "avatar_url": "https://avatars.githubusercontent.com/u/174743446?v=4",
            "description": None
        },
        "sender": {
            "login": "eyolfson",
            "id": 147030,
            "node_id": "MDQ6VXNlcjE0NzAzMA==",
            "avatar_url": "https://avatars.githubusercontent.com/u/147030?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/eyolfson",
            "html_url": "https://github.com/eyolfson",
            "followers_url": "https://api.github.com/users/eyolfson/followers",
            "following_url": "https://api.github.com/users/eyolfson/following{/other_user}",
            "gists_url": "https://api.github.com/users/eyolfson/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/eyolfson/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/eyolfson/subscriptions",
            "organizations_url": "https://api.github.com/users/eyolfson/orgs",
            "repos_url": "https://api.github.com/users/eyolfson/repos",
            "events_url": "https://api.github.com/users/eyolfson/events{/privacy}",
            "received_events_url": "https://api.github.com/users/eyolfson/received_events",
            "type": "User",
            "site_admin": False
        },
        "created": False,
        "deleted": False,
        "forced": False,
        "base_ref": None,
        "compare": "https://github.com/compeng-gg-dev/2024-fall-ece344-eyolfso3/compare/31e989443fc9...742ad44f682e",
        "commits": [
            {
            "id": "742ad44f682ed0bd12eefb9eba72032227a87b12",
            "tree_id": "58f156e351d9cc5b29be064805b7f3b68ab895c6",
            "distinct": True,
            "message": "Update README.md",
            "timestamp": "2024-09-01T15:38:59-04:00",
            "url": "https://github.com/compeng-gg-dev/2024-fall-ece344-eyolfso3/commit/742ad44f682ed0bd12eefb9eba72032227a87b12",
            "author": {
                "name": "Jon Eyolfson",
                "email": "jon@eyolfson.com",
                "username": "eyolfson"
            },
            "committer": {
                "name": "GitHub",
                "email": "noreply@github.com",
                "username": "web-flow"
            },
            "added": [

            ],
            "removed": [

            ],
            "modified": [
                "README.md"
            ]
            }
        ],
        "head_commit": {
            "id": "742ad44f682ed0bd12eefb9eba72032227a87b12",
            "tree_id": "58f156e351d9cc5b29be064805b7f3b68ab895c6",
            "distinct": True,
            "message": "Update README.md",
            "timestamp": "2024-09-01T15:38:59-04:00",
            "url": "https://github.com/compeng-gg-dev/2024-fall-ece344-eyolfso3/commit/742ad44f682ed0bd12eefb9eba72032227a87b12",
            "author": {
            "name": "Jon Eyolfson",
            "email": "jon@eyolfson.com",
            "username": "eyolfson"
            },
            "committer": {
            "name": "GitHub",
            "email": "noreply@github.com",
            "username": "web-flow"
            },
            "added": [

            ],
            "removed": [

            ],
            "modified": [
            "README.md"
            ]
        }
    }
    r = requests.post(
        'http://localhost:8000/api/v0/github/webhook/',
        json=data,
        headers=headers,
    )

if __name__ == '__main__':
    test_webhook()
