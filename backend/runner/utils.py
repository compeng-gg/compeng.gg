import json
import subprocess
import courses.models as course_models

from django.conf import settings

def create_k8s_task(task):
    if not settings.RUNNER_USE_K8S:
        return

    image = "gitea.eyl.io/jon/compeng-backend:latest"
    task_id = task.id

    pod_name = f"{task.head_commit.repository.name}-task-{task_id}"
    container_name = "runrunner"
    namespace = "compeng"

    data = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": pod_name,
            "namespace": namespace,
        },
        "spec": {
            "serviceAccountName": "webhook",
            "volumes": [
                {
                    "name": "github-content",
                    "persistentVolumeClaim": {
                        "claimName": "github-content",
                    },
                },
            ],
            "containers": [
                {
                    "image": image,
                    "imagePullPolicy": "Always",
                    "name": container_name,
                    "command": ["python", "-u", "manage.py", "runrunner", str(task_id)],
                    "volumeMounts": [
                        {
                            "name": "github-content",
                            "mountPath": "/opt/compeng.gg/github_content",
                        },
                    ],
                    "envFrom": [
                        {
                            "secretRef": {
                                "name": "backend",
                            },
                        }
                    ],
                },
            ],
            "restartPolicy": "Never",
            "imagePullSecrets": [
                {
                    "name": "docker",
                },
            ],
        },
    }

    proc = subprocess.Popen(["kubectl", "create", "-f", "-"], stdin=subprocess.PIPE, text=True)
    proc.communicate(input=json.dumps(data))

def create_build_runner(push):
    if not settings.RUNNER_USE_K8S:
        return

    repository = push.repository
    if not repository.offering_runner.exists():
        return

    image = "gitea.eyl.io/jon/compeng-backend:latest"
    push_id = push.id

    pod_name = f"{repository.name}-push-{push_id}"
    container_name = "buildrunner"
    namespace = "compeng"

    data = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": pod_name,
            "namespace": namespace,
        },
        "spec": {
            "volumes": [
                {
                    "name": "docker-volume",
                    "secret": {
                        "secretName": "docker",
                        "items": [
                            {
                                "key": ".dockerconfigjson",
                                "path": "config.json",
                            },
                        ],
                    },
                },
                {
                    "name": "ssh-volume",
                    "secret": {
                        "secretName": f"{repository.name}-deploy",
                        "defaultMode": 256,
                    },
                },
            ],
            "containers": [
                {
                    "image": image,
                    "imagePullPolicy": "Always",
                    "name": container_name,
                    "command": ["python", "-u", "manage.py", "buildrunner", str(push_id)],
                    "volumeMounts": [
                        {
                            "name": "docker-volume",
                            "readOnly": True,
                            "mountPath": "/root/.docker/",
                        },
                        {
                            "name": "ssh-volume",
                            "readOnly": True,
                            "mountPath": "/root/.ssh",
                        },
                    ],
                    "securityContext": {
                        "privileged": True
                    },
                    "envFrom": [
                        {
                            "secretRef": {
                                "name": "backend",
                            },
                        }
                    ],
                },
            ],
            "restartPolicy": "Never",
            "imagePullSecrets": [
                {
                    "name": "docker",
                },
            ],
        },
    }

    proc = subprocess.Popen(["kubectl", "create", "-f", "-"], stdin=subprocess.PIPE, text=True)
    proc.communicate(input=json.dumps(data))

def create_quiz_build_runner(coding_answer_execution: course_models.CodingAnswerExecution) -> None:
    repository = coding_answer_execution.coding_question.repository

    #if not repository.offering_runner.exists():
    #    print("Offering runner does not exist!")
    #    return

    #image = "gitea.eyl.io/jon/compeng-backend:latest"

    process = subprocess.Popen(["python", "manage.py", "quiz_buildrunner", str(coding_answer_execution.id)], stdin=subprocess.PIPE, text=True)
    
    # Wait for the process to complete because this is invoked during a websocket
    process.wait()

    return

    # TODO: actually instantiate a container
    image = "alpine"
    coding_answer_execution_id = coding_answer_execution.id

    pod_name = f"{repository.name}-coding-answer-execution-{coding_answer_execution_id}"
    container_name = "buildrunner"
    namespace = "compeng"

    data = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": pod_name,
            "namespace": namespace,
        },
        "spec": {
            "volumes": [
                {
                    "name": "docker-volume",
                    "secret": {
                        "secretName": "docker",
                        "items": [
                            {
                                "key": ".dockerconfigjson",
                                "path": "config.json",
                            },
                        ],
                    },
                },
                {
                    "name": "ssh-volume",
                    "secret": {
                        "secretName": "deploy-ssh",
                        "defaultMode": 256,
                    },
                },
            ],
            "containers": [
                {
                    "image": image,
                    "imagePullPolicy": "Always",
                    "name": container_name,
                    "command": ["python", "-u", "manage.py", "quiz_buildrunner", str(coding_answer_execution_id)],
                    "volumeMounts": [
                        {
                            "name": "docker-volume",
                            "readOnly": True,
                            "mountPath": "/root/.docker/",
                        },
                        {
                            "name": "ssh-volume",
                            "readOnly": True,
                            "mountPath": "/root/.ssh",
                        },
                    ],
                    "securityContext": {
                        "privileged": True
                    },
                    "envFrom": [
                        {
                            "secretRef": {
                                "name": "backend",
                            },
                        }
                    ],
                },
            ],
            "restartPolicy": "Never",
            "imagePullSecrets": [
                {
                    "name": "docker",
                },
            ],
        },
    }

    print(f"Pod name is {pod_name}")

    proc = subprocess.Popen(["kubectl", "create", "-f", "-"], stdin=subprocess.PIPE, text=True)
    a = proc.communicate(input=json.dumps(data))
    print(a)

    print(proc.stderr)
    print(proc.stdout)

    print("done")
