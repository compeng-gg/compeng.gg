import socket

from django.conf import settings

def send_task(task):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((settings.RUNNER_QUEUE_HOST, settings.RUNNER_QUEUE_PORT))
        s.sendall(str(task.id).encode())
