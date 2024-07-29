from django.db import models
from django.contrib.auth.models import User

class AnonymousMessage(models.Model):
    sent = models.DateTimeField(auto_now_add=True)
    discord_user_id = models.BigIntegerField()
    discord_guild_id = models.BigIntegerField()
    discord_channel_id = models.BigIntegerField()
    discord_message_id = models.BigIntegerField()
    content = models.TextField()
    user = models.ForeignKey(
        User, related_name='anonymous_messages',
        on_delete=models.SET_NULL, blank=True, null=True
    )
    undid = models.BooleanField()

    def __str__(self):
        timestamp = self.sent.isoformat(sep=" ", timespec="seconds")
        if self.user:
            return f'[{timestamp}] {self.user} "{self.content}"'
        else:
            return f'[{timestamp}] "{self.content}"'
