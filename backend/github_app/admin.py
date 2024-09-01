from django.contrib import admin

from .models import (
    Push,
)

@admin.register(Push)
class PushAdmin(admin.ModelAdmin):
    pass
