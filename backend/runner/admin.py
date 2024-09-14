from django.contrib import admin

from . import models

@admin.register(models.Runner)
class RunnerAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created')
    fieldsets = [
        (
            None,
            {
                "fields": ["id", "created", "status", "result"],
            },
        ),
        (
            "GitHub",
            {
                "fields": ["push"],
            },
        ),
    ]