from django.conf import settings
from django.db import models

class QuercusToken(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quercus_token',
    )
    access_token = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.user}'

class QuercusUser(models.Model):
    id = models.BigIntegerField(primary_key=True, unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quercus_user',
    )

    def __str__(self):
        return f'{self.user} ({self.id})'
