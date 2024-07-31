from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from datetime import date

from courses.models import *
from discord_app.rest_api import DiscordRestAPI
from github_app.rest_api import GitHubRestAPI

def create_utoronto_course(name, title):
    utoronto, _ = Institution.objects.get_or_create(
        slug='utoronto',
        defaults={
            'name': 'University of Toronto',
        }
    )
    course, _ = Course.objects.get_or_create(
        institution=utoronto,
        slug=slugify(name),
        defaults={
            'name': name,
            'title': title,
        }
    )
    return course

def create_2024_fall_offering(course):
    name = '2024 Fall'
    start = date(2024, 9, 3)
    end = date(2024, 12, 23)
    offering, _ = Offering.objects.get_or_create(
        course=course,
        slug=slugify(name),
        defaults={
            'name': name,
            'start': start,
            'end': end,
            'active': True,
        }
    )
    return offering

def create_default_roles(offering):
    Role.objects.get_or_create(
        offering=offering,
        kind=Role.Kind.INSTRUCTOR,
    )
    Role.objects.get_or_create(
        offering=offering,
        kind=Role.Kind.TA,
    )
    Role.objects.get_or_create(
        offering=offering,
        kind=Role.Kind.STUDENT,
    )

def create_discord_roles(offering):
    api = DiscordRestAPI()

    roles = Role.objects.filter(offering=offering)
    lookup = {}
    for role in roles:
        lookup[str(role)] = role

    for discord_role in api.get_guild_roles_for_guild():
        name = discord_role['name']
        if not name in lookup:
            continue
        role = lookup[name]
        discord_role_id = int(discord_role['id'])
        if not role.discord_role_id is None:
            assert role.discord_role_id == discord_role_id
        else:
            role.discord_role_id = discord_role_id
            role.save()

    for name, role in lookup.items():
        if not role.discord_role_id is None:
            continue
        response = api.create_guild_role_for_guild(
            name, DiscordRestAPI.COLOR_RED
        )
        role.discord_role_id = response['id']
        role.save()

def create_github_teams(offering):
    api = GitHubRestAPI()

    roles = Role.objects.filter(offering=offering)
    for role in roles:
        name = str(role)
        slug = slugify(name)
        try:
            response = api.get_team_for_org(slug)
            assert slug == response['slug']
            if role.github_team_slug == '':
                role.github_team_slug = slug
                role.save()
        except:
            response = api.create_team_for_org(name)
            assert slug == response['slug']
            offering.github_team_slug = slug
            offering.save()

class Command(BaseCommand):
    help = "Populate Courses Test Models"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        ece344 = create_utoronto_course('ECE344', 'Operating Systems')
        ece454 = create_utoronto_course('ECE454', 'Computer Systems Programming')
        ece344_offering = create_2024_fall_offering(ece344)
        ece454_offering = create_2024_fall_offering(ece454)
        create_default_roles(ece344_offering)
        create_discord_roles(ece344_offering)
        create_github_teams(ece344_offering)
        create_default_roles(ece454_offering)
        create_discord_roles(ece454_offering)
        create_github_teams(ece454_offering)
