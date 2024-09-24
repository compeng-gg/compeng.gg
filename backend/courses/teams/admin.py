from django.contrib import admin
from . import models

@admin.register(models.Team)
class Teams(admin.ModelAdmin):
    pass
