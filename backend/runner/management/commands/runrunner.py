import json
import shlex
import subprocess
import sys
import time

from courses.utils import populate_assignment_grades
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
        image = f"{settings.RUNNER_IMAGE_REPO}/{task.runner.image}"
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
                # The file could not be in the repository
                if not full_path:
                    continue
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


        data = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": pod_name,
                "namespace": namespace,
            },
            "spec": {
                "containers": [
                    {
                        "image": image,
                        "imagePullPolicy": "Always",
                        "name": container_name,
                        "command": command,
                        "volumeMounts": volume_mounts,
                        "resources": {
                            "requests": {
                                "memory": "100Mi",
                            },
                            "limits": {
                                "memory": "200Mi"
                            },
                        },
                    },
                ],
                "imagePullSecrets": settings.RUNNER_IMAGE_PULL_SECRETS,
                "restartPolicy": "Never",
                "volumes": [
                    {
                        "name": "github-content",
                        "persistentVolumeClaim": {
                            "claimName": "github-content",
                        },
                    },
                ],
            },
        }

        # TODO: remove
        # if task.runner.image == "2025-winter-ece353-runner:latest" and task.runner.command == "/workspace/lab6/grade.py":
        #    data["spec"]["containers"][0]["securityContext"] = {
        #        "privileged": True,
        #    }

        p = subprocess.run(
            ["kubectl", "create", "-f", "-"],
            check=True, input=json.dumps(data), text=True
        )
        out_of_memory = False
        while True:
            p = subprocess.run(
                ["kubectl", "get", "pod", pod_name, "-o", "json"],
                capture_output=True, text=True,
            )
            output = json.loads(p.stdout)
            status = output["status"]
            if not "containerStatuses" in status:
                time.sleep(0.1)
                continue
            state = status["containerStatuses"][0]["state"]
            if "terminated" in state:
                terminated = state["terminated"]
                if "reason" in terminated and terminated["reason"] == "OOMKilled":
                    out_of_memory = True
                exit_code = terminated["exitCode"]
                break
            time.sleep(0.1)

        p = subprocess.run(
            ["kubectl", "logs", pod_name],
            capture_output=True, text=True,
        )
        subprocess.run(
            ["kubectl", "delete", "pod", pod_name],
            check=True,
        )

        if out_of_memory:
            task.result = {"error": "out-of-memory"}
            task.status = Task.Status.FAILURE
            task.save()
            self.stdout.write(f'{task} failure (out-of-memory)')
            sys.exit(0)

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

        if exit_code == 0:
            task.status = Task.Status.SUCCESS
            self.stdout.write(f'{task} success')
        else:
            task.status = Task.Status.FAILURE
            self.stdout.write(f'{task} failure')
        task.save()

        if task.status == Task.Status.SUCCESS:
            populate_assignment_grades(task)
