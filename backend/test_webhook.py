import requests

from compeng_gg import settings

def test_webhook():
    headers = {
        'X-Gitlab-Token': settings.WEBHOOK_TOKEN,
        'X-Gitlab-Event': 'Push Hook',
    }
    data = {
        'object_kind': 'push',
        'event_name': 'push',
        'before': '95790bf891e76fee5e1747ab589903a6a1f80f22',
        'after': 'da1560886d4f094c3e6c9ef40349f7d38b5d27d7',
        'ref': 'refs/heads/master',
        'ref_protected': True,
        'checkout_sha': 'da1560886d4f094c3e6c9ef40349f7d38b5d27d7',
        'message': 'Hello World',
        'user_id': 1,
        'user_name': 'John Smith',
        'user_email': 'john@example.com',
        'user_avatar': 'https://s.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=8://s.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=80',
        'project_id': 15,
        'project': {
            'id': 15,
            'name': 'gitlab',
            'description': '',
            'web_url': 'http://test.example.com/gitlab/gitlab',
            'avatar_url': 'https://s.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=8://s.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=80',
            'git_ssh_url': 'git@test.example.com:gitlab/gitlab.git',
            'git_http_url': 'http://test.example.com/gitlab/gitlab.git',
            'namespace': 'gitlab',
            'visibility_level': 0,
            'path_with_namespace': 'gitlab/gitlab',
            'default_branch': 'master'
        },
        'commits': [
            {
                'id': 'c5feabde2d8cd023215af4d2ceeb7a64839fc428',
                'message': 'Add simple search to projects in public area\n\ncommit message body',
                'title': 'Add simple search to projects in public area',
                'timestamp': '2013-05-13T18:18:08+00:00',
                'url': 'https://test.example.com/gitlab/gitlab/-/commit/c5feabde2d8cd023215af4d2ceeb7a64839fc428',
                'author': {
                    'name': 'Test User',
                    'email': 'test@example.com'
                }
            }
        ],
        'total_commits_count': 1,
        'push_options': {
            'ci': {
                'skip': True
            }
        }
    }
    r = requests.post(
        'http://localhost:8000/webhook/endpoint/',
        json=data,
        headers=headers,
    )

if __name__ == '__main__':
    test_webhook()
