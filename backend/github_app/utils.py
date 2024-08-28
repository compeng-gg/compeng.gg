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
