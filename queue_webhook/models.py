from django.db import models

class Task(models.Model):

    class Status(models.IntegerChoices):
        QUEUED = 1
        IN_PROGRESS = 2
        SUCCESS = 3
        FAILURE = 4

    status = models.IntegerField(choices=Status.choices)
    created = models.DateTimeField(auto_now_add=True)

    data = models.JSONField(unique=True)
    result = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'Task {self.id}'

    class Meta:
        ordering = ['-created']
