from django.contrib import admin
from . import models

@admin.register(models.TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'team')
    list_display_links = ('enrollment', 'team')
    
    pass