from django.contrib import admin
from .models import (
    AnonymousMessage,
)

@admin.register(AnonymousMessage)
class AnonymousMessageAdmin(admin.ModelAdmin):
    pass
