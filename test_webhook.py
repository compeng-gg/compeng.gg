import requests

from compeng_gg import settings

def test_webhook():
    headers = {
        'X-Gitlab-Token': settings.QUEUE_SECRET_TOKEN,
        'X-Gitlab-Event': 'Push Hook',
    }
    data = {
        'object_kind': 'push',
        'event_name': 'push',
    }
    r = requests.post(
        'http://localhost:8000/webhook/endpoint/',
        json=data,
        headers=headers,
    )

if __name__ == '__main__':
    test_webhook()
