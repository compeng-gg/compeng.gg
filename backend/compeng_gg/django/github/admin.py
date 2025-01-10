import json

from compeng_gg.django.github.models import (
    Commit,
    Delivery,
    Hook,
    Organization,
    Path,
    Push,
    Repository,
    Team,
    User,
)
from django.contrib import admin
from django.utils.safestring import SafeText

@admin.register(Commit)
class CommitAdmin(admin.ModelAdmin):
    readonly_fields = [
        "repository",
        "sha1",
        "paths_added",
        "paths_modified",
        "paths_removed",
    ]

@admin.register(Hook)
class HookAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "installation_target"]

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    date_hierarchy = "received"
    readonly_fields = ["content_object", "hook", "received", "event", "_payload"]

    def _payload(self, instance):
        return SafeText(f"<pre>{json.dumps(instance.payload, indent=4)}</pre>")

    _payload.short_description = "Payload"

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    readonly_fields = ["login", "members"]

@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    readonly_fields = ["repository", "relative"]

@admin.register(Push)
class PushAdmin(admin.ModelAdmin):
    readonly_fields = ["sender", "repository", "ref", "head_commit", "commits"]

@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    readonly_fields = ["name", "full_name", "owner"]

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    readonly_fields = ["organization", "slug", "name", "members"]

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ["login"]
