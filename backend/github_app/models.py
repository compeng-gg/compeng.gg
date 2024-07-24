from django.db import models

class Push(models.Model):
    received = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(unique=True)
