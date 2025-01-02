import json
import subprocess

from django.conf import settings

def create_build_runner(push):
    if not settings.RUNNER_USE_K8S:
        return

    image = "gitea.eyl.io/jon/compeng-backend:latest"
    push_id = push.id

    repository = push.repository

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
