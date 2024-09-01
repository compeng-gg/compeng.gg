from django.db import models

class Push(models.Model):
    received = models.DateTimeField(auto_now_add=True)
    delivery = models.CharField(max_length=255, unique=True)
    payload = models.JSONField()
