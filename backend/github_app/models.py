from django.db import models

class Push(models.Model):
    received = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(unique=True)
