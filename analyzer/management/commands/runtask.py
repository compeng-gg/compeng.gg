from django.core.management.base import BaseCommand, CommandError

from analyzer.models import Task

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
