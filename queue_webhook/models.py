from django.db import models

class Task(models.Model):

    class Status(models.IntegerChoices):
        QUEUED = 1
        IN_PROGRESS = 2
        SUCCESS = 3
        FAILURE = 4

    status = models.IntegerField(choices=Status.choices)
    project_id = models.IntegerField()
    ref = models.TextField()
    before = models.CharField(max_length=40)
    after = models.CharField(max_length=40)

    def __str__(self):
        return f'Task {self.id}'
