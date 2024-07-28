from social_core.backends.discord import DiscordOAuth2
from social_core.backends.github import GithubOAuth2
from social_core.backends.gitlab import GitLabOAuth2

class LaForgeBackend(GitLabOAuth2):
    name = 'laforge'
    API_URL = "https://laforge.eecg.utoronto.ca"
    STATE_PARAMETER = False

class CustomDiscordOAuth2(DiscordOAuth2):
    STATE_PARAMETER = False

class CustomGithubOAuth2(GithubOAuth2):
    STATE_PARAMETER = False
