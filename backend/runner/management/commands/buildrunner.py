import pathlib
import subprocess

from compeng_gg.django.github.models import Push
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("push_id", type=int)

    def handle(self, *args, **options):
        push_id = options["push_id"]
        try:
            push = Push.objects.get(id=push_id)
        except Push.DoesNotExist:
            raise CommandError(f"Push {push_id} does not exist")

        repository = push.repository

        tmp_dir = pathlib.Path("/tmp")
        subprocess.run(
            ["git", "clone", "--depth", "1", f"git@github.com:{repository.full_name}"],
            check=True, cwd=tmp_dir,
        )

        repo_dir = tmp_dir / repository.name
        tag = f"{settings.RUNNER_IMAGE_REPO}/{repository.name}:latest"
        subprocess.run(["podman", "build", "-t", tag, "."], cwd=repo_dir)
        subprocess.run(["podman", "push", tag])
