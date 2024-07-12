from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Offering, Role

from github.rest_api import GitHubRestAPI

@receiver(post_save, sender=Offering)
def offering_post_save(sender, instance=None, **kwargs):
    if not instance:
        return

    Role.objects.get_or_create(
        kind=Role.Kind.INSTRUCTOR,
        offering=instance,
    )
    Role.objects.get_or_create(
        kind=Role.Kind.TA,
        offering=instance,
    )
    Role.objects.get_or_create(
        kind=Role.Kind.STUDENT,
        offering=instance,
    )

@receiver(post_save, sender=Role)
def role_post_save(sender, instance=None, **kwargs):
    if not instance:
        return

    if instance.discord_role_id is None:
        # TODO: Add Discord role
        pass
    
    if instance.github_team_slug == '':
        api = GitHubRestAPI()
        response = api.create_team_for_org(str(instance))
        if response is None:
            team_slug = slugify(str(instance))
            response = api.get_team_for_org(team_slug)
        instance.github_team_slug = response['slug']
        instance.save()
