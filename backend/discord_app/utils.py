from compeng_gg.auth import get_access_token, get_uid
from courses.models import Institution
from discord_app.rest_api import DiscordRestAPI

def add_discord_role_for_enrollment(enrollment):
    discord_user_id = get_uid('discord', enrollment.user)
    role = enrollment.role
    utoronto = Institution.objects.get(slug='utoronto')
    discord_role_id = role.discord_role_id

    api = DiscordRestAPI()
    api.add_guild_member_role_for_guild(discord_user_id, discord_role_id)
    if role.kind == role.Kind.INSTRUCTOR:
        api.add_guild_member_role_for_guild(
            discord_user_id, utoronto.faculty_discord_role_id
        )
    elif role.kind == role.Kind.TA:
        api.add_guild_member_role_for_guild(
            discord_user_id, utoronto.grad_student_discord_role_id
        )
    elif role.kind == role.Kind.STUDENT:
        num = role.offering.course.slug[3]
        if num == '1':
            api.add_guild_member_role_for_guild(
                discord_user_id, utoronto.first_year_discord_role_id
            )
        elif num == '2':
            api.add_guild_member_role_for_guild(
                discord_user_id, utoronto.second_year_discord_role_id
            )
        elif num == '3':
            api.add_guild_member_role_for_guild(
                discord_user_id, utoronto.third_year_discord_role_id
            )
        elif num == '4':
            api.add_guild_member_role_for_guild(
                discord_user_id, utoronto.fourth_year_discord_role_id
            )

def remove_discord_role_for_enrollment(enrollment):
    discord_user_id = get_uid('discord', enrollment.user)
    role = enrollment.role
    discord_role_id = role.discord_role_id
    api = DiscordRestAPI()
    api.remove_guild_member_role_for_guild(discord_user_id, discord_role_id)

def add_discord_roles(user):
    discord_user_id = get_uid('discord', user)
    utoronto = Institution.objects.get(slug='utoronto')

    api = DiscordRestAPI()
    api.add_guild_member_role_for_guild(
        discord_user_id, utoronto.verified_discord_role_id
    )

    for enrollment in user.enrollment_set.all():
        add_discord_role_for_enrollment(enrollment)

def add_to_discord_server(user):
    access_token = get_access_token('discord', user)
    discord_user_id = get_uid('discord', user)
    api = DiscordRestAPI()
    api.add_guild_member_for_guild(discord_user_id, access_token)
    add_discord_roles(user)
