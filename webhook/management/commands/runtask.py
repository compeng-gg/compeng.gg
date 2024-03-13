from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from social_django.models import UserSocialAuth
from webhook.models import Task
from social_django.utils import load_strategy

import os
import pathlib
import requests
import subprocess
import urllib.parse

class GitLabAPI:

    def __init__(self, api_url, access_token):
        self.api_url = api_url
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
        }

    def get_request(self, url):
        return requests.get(f'{self.api_url}{url}', headers=self.headers)

    def get(self, url):
        return self.get_request(url).json()

    def get_raw_file(self, project_id, file_path, ref):
        escaped_file_path = urllib.parse.quote(bytes(file_path), safe='')
        response = self.get_request(f'/projects/{project_id}/repository/files/{escaped_file_path}/raw?ref={ref}')
        if response.status_code != 200:
            raise CommandError(f"File '{file_path}' not found")
        return response.text

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("task_id", type=int)

    def handle(self, *args, **options):
        task_id = options["task_id"]
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise CommandError(f'Task {task_id} does not exist')

        task.status = Task.Status.IN_PROGRESS
        task.save()
        self.stdout.write(f'{task} in progress')

        try:
            social = UserSocialAuth.objects.get(provider='laforge', uid=task.data['user_id'])
        except UserSocialAuth.DoesNotExist:
            raise CommandError(f'Task does not have a valid user')

        strategy = load_strategy()
        access_token = social.get_access_token(strategy)
        backend = social.get_backend_instance(strategy)
        api_url = backend.api_url('/api/v4/user')

        gitlab = GitLabAPI(backend.api_url('/api/v4'), access_token)
        project_id = task.data['project_id']
        checkout_sha = task.data['checkout_sha']

        v1_repo_path = pathlib.Path('pht/src/hash-table-v1.c')
        v2_repo_path = pathlib.Path('pht/src/hash-table-v2.c')

        lab5_dir = settings.BASE_DIR / 'task' / 'lab5' / str(project_id) / checkout_sha
        os.makedirs(lab5_dir, exist_ok=True)
        v1_path = lab5_dir / v1_repo_path.name
        with open(v1_path, 'w') as f:
            f.write(gitlab.get_raw_file(project_id, v1_repo_path, checkout_sha))
        v2_path = lab5_dir / v2_repo_path.name
        with open(v2_path, 'w') as f:
            f.write(gitlab.get_raw_file(project_id, v2_repo_path, checkout_sha))

        cmd = [
            'docker',
            'run',
            '--rm',
            '-v', f'{v1_path}:/workspace/{v1_repo_path}',
            '-v', f'{v2_path}:/workspace/{v2_repo_path}',
            '-w', '/workspace/pht',
            'ece344:latest',
            #'sh', '-c', 'meson setup build >/dev/null && meson compile -C build >/dev/null && build/pht-tester -t 4 -s 15000',
            'sh', '-c', 'meson setup build >/dev/null && meson compile -C build >/dev/null && build/pht-tester -t 4 -s 75000',
        ]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        try:
            lines = p.stdout.splitlines()
            category, value, unit = lines[1].rsplit(maxsplit=2)
            assert category == 'Hash table base:' and unit == 'usec'
            base_value = int(value)

            start, value, end = lines[2].rsplit(maxsplit=2)
            assert start == '  -' and end == 'missing'
            assert value == '0'

            category, value, unit = lines[3].rsplit(maxsplit=2)
            assert category == 'Hash table v1:' and unit == 'usec'
            v1_value = int(value)

            start, value, end = lines[4].rsplit(maxsplit=2)
            assert start == '  -' and end == 'missing'
            v1_sanity = value == '0'

            category, value, unit = lines[5].rsplit(maxsplit=2)
            assert category == 'Hash table v2:' and unit == 'usec'
            v2_value = int(value)

            start, value, end = lines[6].rsplit(maxsplit=2)
            assert start == '  -' and end == 'missing'
            v2_sanity = value == '0'
        except Exception as e:
            task.result = {
                'stdout': p.stdout,
            }
            task.save()
            exit(1)

        cmd = [
            'docker',
            'run',
            '--rm',
            '--privileged', # This is bad, figure out how to disable ALSR in the container without this later, needs to be disabled for TSan
            '-v', f'{v1_path}:/workspace/{v1_repo_path}',
            '-v', f'{v2_path}:/workspace/{v2_repo_path}',
            '-w', '/workspace/pht',
            'ece344:latest',
            'sh', '-c', 'meson setup -Db_sanitize=thread build >/dev/null && meson compile -C build >/dev/null && setarch aarch64 --addr-no-randomize build/pht-tester -t 4 -s 1000',
        ]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        thread_sanitizer = None
        if p.stderr:
            last_line = p.stderr.splitlines()[-1]
            if last_line.startswith('ThreadSanitizer'):
                thread_sanitizer = last_line

        p = subprocess.run([
            'docker',
            'run',
            '--rm',
            '-v', f'{v1_path}:/workspace/{v1_repo_path}',
            '-v', f'{v2_path}:/workspace/{v2_repo_path}',
            '-w', '/workspace/pht',
            'ece344:latest',
            'sh', '-c', 'meson setup build >/dev/null && meson compile -C build >/dev/null && valgrind --error-exitcode=1 build/pht-tester -t 4 -s 10000',
        ], capture_output=True, text=True, timeout=30)

        valgrind = p.returncode == 0

        v1_relative = base_value / v1_value
        v2_relative = base_value / v2_value

        v1_expected = v1_relative > 0.3 and v1_relative < 0.8
        v2_expected = v2_relative > 2 and v2_relative < 4

        tsan_okay = thread_sanitizer is None
        grade = 0
        if v1_expected:
            grade += 8
        if v2_expected:
            grade += 8
        if v1_sanity:
            grade += 10
        if v2_sanity:
            grade += 10
        if valgrind:
            grade += 4
        if v1_expected and v2_expected and tsan_okay:
            grade += 60
        task.result = {
            'base_value': base_value,
            'v1_value': v1_value,
            'v2_value': v2_value,
            'valgrind': valgrind,
            'base_seconds': f"{base_value / 1000000:.2f} s",
            'v1_seconds': f"{v1_value / 1000000:.2f} s",
            'v2_seconds': f"{v2_value / 1000000:.2f} s",
            'v1_relative': v1_relative,
            'v2_relative': v2_relative,
            'v1_expected': v1_expected,
            'v2_expected': v2_expected,
            'v1_sanity': v1_sanity,
            'v2_sanity': v2_sanity,
            'cores': 4,
            'thread_sanitizer': thread_sanitizer,
            'grade': grade,
        }
        if not valgrind:
            task.result['valgrind_log'] = p.stderr
        task.save()
