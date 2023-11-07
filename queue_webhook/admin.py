from django.contrib import admin
from . import models

@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    fieldsets = [
        (
            None,
            {
                "fields": ["id", "status", "created", "result"],
            },
        ),
        (
            "GitLab",
            {
                "fields": ["data"],
            },
        ),
    ]
