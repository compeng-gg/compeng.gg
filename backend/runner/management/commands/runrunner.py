import json
import shlex
import subprocess
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from github_app.utils import get_dir, get_file
from runner.models import Task

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

        head_commit = task.head_commit
        repository = head_commit.repository
        image = f"gitea.eyl.io/jon/{task.runner.image}"
        namespace = "compeng"
        command = shlex.split(task.runner.command)
        pod_name = f"{repository.name}-task-{task_id}-runner"
        container_name = "runner"

        assignment_task = task.assignmenttask_set.get() # TODO: this is bad
        # If this is true, it should be a OneToOneField, if not it should
        # be more flexible. Ideally separate the files to mount.
        assignment = assignment_task.assignment

        volume_mounts = []
        for file_path in assignment.files:
            if not file_path.endswith('/'):
                full_path = get_file(
                    repository.name, file_path, head_commit.sha1,
                )
            else:
                full_path = get_dir(
                    repository.name, file_path, head_commit.sha1,
                )
            relative = full_path.relative_to(settings.GITHUB_CONTENT_DIR)
            volume_mounts.append({
                "name": "github-content",
                "subPath": str(relative),
                "mountPath": f"/workspace/{file_path}",
            })

        overrides = {
            "spec": {
                "imagePullSecrets": [
                    {
                        "name": "docker",
                    },
                ],
                "containers": [
                    {
                        "image": image,
                        "imagePullPolicy": "Always",
                        "name": "runner",
                        "command": command,
                        "volumeMounts": volume_mounts,
                    },
                ],
                "volumes": [
                    {
                        "name": "github-content",
                        "persistentVolumeClaim": {
                            "claimName": "github-content",
                        },
                    },
                ],
            }
        }

        p = subprocess.run(
            [
                "kubectl", "run", pod_name, "-q", "-i", "--rm",
                "--image", image, "--restart=Never",
                f"--overrides={json.dumps(overrides)}",
            ],
            capture_output=True, text=True,
        )

        try:
            task.result = json.loads(p.stdout)
        except:
            task.result = {"error": "contact-jon"}

            self.stdout.write(f'stdout: {p.stdout}')
            self.stdout.write(f'stderr: {p.stderr}')
            task.status = Task.Status.FAILURE
            self.stdout.write(f'{task} failure')
            task.save()
            sys.exit(1)

        if p.stderr != '':
            self.stderr.write(p.stderr)

        if p.returncode == 0:
            task.status = Task.Status.SUCCESS
            self.stdout.write(f'{task} success')
        else:
            task.status = Task.Status.FAILURE
            self.stdout.write(f'{task} failure')
        task.save()
