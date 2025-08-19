from compeng_gg.django.github.models import Commit
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

class Bot(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    head_commit = models.ForeignKey(
        Commit,
        on_delete=models.CASCADE,
    )
    rating = models.IntegerField()
    active = models.BooleanField()

    def __str__(self):
        return f"Bot{user.id}-{head_commit[:8]}"

class Match(models.Model):

    class Result(models.TextChoices):
        WIN = "W", _("Win")
        LOSS = "L", _("Loss")
        DRAW = "D", _("Draw")

    bot = models.ForeignKey(
        Bot,
        on_delete=models.CASCADE,
        related_name="matches",
    )
    opponent = models.ForeignKey(
        Bot,
        on_delete=models.CASCADE,
    )
    played_at = models.DateTimeField()
    result = models.CharField(
        max_length=1,
        choices=Result,
    )
    rating_change = models.IntegerField()

    class Meta:
        verbose_name_plural = "matches"
