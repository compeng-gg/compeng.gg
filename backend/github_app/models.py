from django.db import models

class Push(models.Model):
    received = models.DateTimeField(auto_now_add=True)
    event = models.JSONField(unique=True)
