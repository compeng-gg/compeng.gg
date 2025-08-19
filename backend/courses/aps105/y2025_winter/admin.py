from django.contrib import admin

from .models import (
    Bot,
    Match,
)

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    pass

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    pass


