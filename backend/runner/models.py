from django.db import models
from github_app.models import Push

class Runner(models.Model):

    image = models.CharField(max_length=255)
    command = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.image} {self.command}'

class Task(models.Model):

    class Status(models.IntegerChoices):
        QUEUED = 1
        IN_PROGRESS = 2
        SUCCESS = 3
        FAILURE = 4

    status = models.IntegerField(choices=Status.choices)
    created = models.DateTimeField(auto_now_add=True)
    push = models.ForeignKey(Push, on_delete=models.CASCADE)
    runner = models.ForeignKey(Runner, on_delete=models.CASCADE)
    result = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'Task {self.id}'

    class Meta:
        ordering = ['-created']
