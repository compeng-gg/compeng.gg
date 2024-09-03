from github_app.rest_api import GitHubRestAPI

def add_github_team_membership_for_enrollment(enrollment):
    user = enrollment.user
    social = user.social_auth.get(provider='github')
    github_username = social.extra_data['login']
    role = enrollment.role
    github_team_slug = role.github_team_slug
    api = GitHubRestAPI()
    api.add_team_membership_for_org(github_team_slug, github_username)

def add_github_team_membership(user):
    for enrollment in user.enrollment_set.all():
        add_github_team_membership_for_enrollment(enrollment)

def create_fork(course_slug, user):
    from courses.models import Enrollment, Role
    from compeng_gg.auth import get_uid
    from django.core.exceptions import ObjectDoesNotExist
    role = Role.objects.get(kind=Role.Kind.STUDENT, offering__course__slug=course_slug)
    try:
        Enrollment.objects.get(user=user, role=role)
    except Enrollment.DoesNotExist:
        return
    try:
        get_uid('github', user)
    except ObjectDoesNotExist:
        return
    api = GitHubRestAPI()
    student_repo_name = f'2024-fall-{course_slug}-student'
    repo_name = f'2024-fall-{course_slug}-{user.username}' # TODO
    api.create_fork_for_org(student_repo_name,
        name=repo_name
    )
    github_username = user.social_auth.get(provider='github').extra_data['login']
    api.add_repository_collaborator_for_org(repo_name, github_username, permissions='push')
    import json
    offering = role.offering
    for role in offering.role_set.all():
        if role.kind == Role.Kind.INSTRUCTOR:
            api.add_team_repository_permissions_for_org(
                role.github_team_slug,
                repo_name,
                permission='pull'
            )
        elif role.kind == Role.Kind.TA:
            api.add_team_repository_permissions_for_org(
                role.github_team_slug,
                repo_name,
                permission='pull'
            )
        elif role.kind == Role.Kind.STUDENT:
            api.add_remove_repository_permissions_for_org(
                role.github_team_slug,
                repo_name,
            )
