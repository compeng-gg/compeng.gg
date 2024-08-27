from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from datetime import date

from courses.models import *
from discord_app.rest_api import DiscordRestAPI
from github_app.rest_api import GitHubRestAPI

def get_or_create_utoronto():
    utoronto, _ = Institution.objects.get_or_create(
        slug='utoronto',
        defaults={
            'name': 'University of Toronto',
        }
    )
    return utoronto

def create_utoronto_course(name, title):
    utoronto = get_or_create_utoronto()
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

def create_2024_winter_offering(course):
    name = '2024 Winter'
    start = date(2024, 1, 8)
    end = date(2024, 4, 30)
    offering, _ = Offering.objects.get_or_create(
        course=course,
        slug=slugify(name),
        defaults={
            'name': name,
            'start': start,
            'end': end,
            'active': False,
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

def get_color_for_role(role, student_color):
    if role.kind == Role.Kind.INSTRUCTOR:
        color = DiscordRestAPI.COLOR_RED
    elif role.kind == Role.Kind.TA:
        color = DiscordRestAPI.COLOR_YELLOW
    else:
        color = student_color
    return color

def create_discord_roles(offering, student_color=DiscordRestAPI.COLOR_MAGENTA):
    api = DiscordRestAPI()

    roles = Role.objects.filter(offering=offering)
    lookup = {}
    found = set()
    for role in roles:
        lookup[str(role)] = role

    for discord_role in api.get_guild_roles_for_guild():
        name = discord_role['name']
        if not name in lookup:
            continue
        found.add(name)
        role = lookup[name]
        discord_role_id = int(discord_role['id'])
        if not role.discord_role_id is None:
            assert role.discord_role_id == discord_role_id
            color = get_color_for_role(role, student_color)
            if discord_role['color'] != color:
                api.modify_guild_role_for_guild(discord_role_id, color=color)
        else:
            role.discord_role_id = discord_role_id
            role.save()

    for name, role in lookup.items():
        if not role.discord_role_id is None and name in found:
            continue
        color = get_color_for_role(role, student_color)
        response = api.create_guild_role_for_guild(name, color)
        discord_role_id = int(response['id'])
        role.discord_role_id = discord_role_id
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

def create_utoronto_roles():
    api = DiscordRestAPI()

    utoronto = get_or_create_utoronto()
    lookup = {
        'Faculty':
            ('faculty_discord_role_id', DiscordRestAPI.COLOR_RED),
        'Grad Student':
            ('grad_student_discord_role_id', DiscordRestAPI.COLOR_YELLOW),
        '4th Year':
            ('fourth_year_discord_role_id', DiscordRestAPI.COLOR_PURPLE),
        '3rd Year':
            ('third_year_discord_role_id', DiscordRestAPI.COLOR_BLUE),
        '2nd Year':
            ('second_year_discord_role_id', DiscordRestAPI.COLOR_CYAN),
        '1st Year':
            ('first_year_discord_role_id', DiscordRestAPI.COLOR_MAGENTA),
        'Verified':
            ('verified_discord_role_id', DiscordRestAPI.COLOR_GREEN),
    }
    found = set()

    for discord_role in api.get_guild_roles_for_guild():
        name = discord_role['name']
        if not name in lookup:
            continue
        found.add(name)
        discord_role_id = int(discord_role['id'])
        field_name, color = lookup[name]
        model_discord_role_id = getattr(utoronto, field_name)
        if not model_discord_role_id is None:
            assert model_discord_role_id == discord_role_id
            if discord_role['color'] != color:
                api.modify_guild_role_for_guild(discord_role_id, color=color)
        else:
            setattr(utoronto, field_name, discord_role_id)
            utoronto.save()

    for name, (field_name, color) in lookup.items():
        model_discord_role_id = getattr(utoronto, field_name)
        if not model_discord_role_id is None and name in found:
            continue
        response = api.create_guild_role_for_guild(name, color, hoist=True)
        discord_role_id = int(response['id'])
        setattr(utoronto, field_name, discord_role_id)
        utoronto.save()

class Command(BaseCommand):
    help = "Populate Courses Test Models"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        create_utoronto_roles()
        ece353 = create_utoronto_course('ECE353', 'Systems Software')
        ece353_offering = create_2024_winter_offering(ece353)
        create_default_roles(ece353_offering)
        create_discord_roles(
            ece353_offering,
            student_color=DiscordRestAPI.COLOR_BLUE
        )
        ece344 = create_utoronto_course('ECE344', 'Operating Systems')
        ece454 = create_utoronto_course('ECE454', 'Computer Systems Programming')
        ece344_offering = create_2024_fall_offering(ece344)
        ece454_offering = create_2024_fall_offering(ece454)
        create_default_roles(ece344_offering)
        create_discord_roles(
            ece344_offering,
            student_color=DiscordRestAPI.COLOR_BLUE
        )
        create_github_teams(ece344_offering)
        create_default_roles(ece454_offering)
        create_discord_roles(
            ece454_offering,
            student_color=DiscordRestAPI.COLOR_PURPLE
        )
        create_github_teams(ece454_offering)
