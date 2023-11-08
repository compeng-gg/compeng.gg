from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import socket
import subprocess
import threading

from queue_webhook.models import Task
from queue_webhook.socket import HOST, PORT

class Command(BaseCommand):

    def run_task(self, task):
        cmd = ['ssh', 'canoe-0', '/opt/compeng.gg/venv/bin/python', '/opt/compeng.gg/manage.py', 'runtask', str(task.id)]
        if False:
            cmd = ['python', 'manage.py', 'runtask', str(task.id)]

        p = subprocess.run(cmd, cwd=settings.BASE_DIR)
        if p.returncode == 0:
            task.status = Task.Status.SUCCESS
            self.stdout.write(f'{task} success')
        else:
            task.status = Task.Status.FAILURE
            self.stdout.write(f'{task} failure')
        task.save()

    def run(self, conn):
        with conn:
            data = conn.recv(8)
            task_id = int.from_bytes(data)

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return
        self.run_task(task)

    def _socket_listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen()
        return s

    def handle(self, *args, **options):
        for task in Task.objects.filter(status=Task.Status.QUEUED):
            t = threading.Thread(target=Command.run_task, args=(self, task))
            t.start()

        try:
            s = self._socket_listen()
            self.stdout.write(self.style.SUCCESS(f'Listening on {HOST}:{PORT}'))
        except OSError as err:
            raise CommandError(f'Socket failed: {err}')

        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=Command.run, args=(self, conn))
            t.start()

        s.close()
