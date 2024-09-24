from django.conf import settings
from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext_lazy as _

from runner.models import Runner, Task      


class Team(models.Model):
    name = models.CharField(max_length=50)
    teamID = models.IntegerField()
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)
    offering = models.ForeignKey(
        Offering,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
