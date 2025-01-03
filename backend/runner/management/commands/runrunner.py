import json
import shlex
import subprocess

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

        image = f"gitea.eyl.io/jon/{task.runner.image}"
        namespace = "compeng"
        command = shlex.split(task.runner.command)
        pod_name = f"{task.head_commit.repository.name}-task-{task_id}-runner"
        container_name = "runner"

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
            task.result = {"error": "contact-ta"}

        if p.stderr != '':
            self.stderr.write(p.stderr)

        if p.returncode == 0:
            task.status = Task.Status.SUCCESS
            self.stdout.write(f'{task} success')
        else:
            task.status = Task.Status.FAILURE
            self.stdout.write(f'{task} failure')
        task.save()
