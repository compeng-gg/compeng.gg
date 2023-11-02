from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import socket
import subprocess
import threading

from analyzer.models import Task
from analyzer.socket import HOST, PORT

class Command(BaseCommand):

    def run(self, conn):
        with conn:
            data = conn.recv(8)
            task_id = int.from_bytes(data)

        task = Task.objects.get(id=task_id)
        task.status = Task.Status.QUEUED
        task.save()
        self.stdout.write(f'{task} queued')

        p = subprocess.run(['python', 'manage.py', 'runtask', str(task_id)],
                           cwd=settings.BASE_DIR)
        if p.returncode == 0:
            task.status = Task.Status.SUCCESS
            self.stdout.write(f'{task} success')
        else:
            task.status = Task.Status.FAILURE
            self.stdout.write(f'{task} failure')
        task.save()

    def _socket_listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen()
        return s

    def handle(self, *args, **options):
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
