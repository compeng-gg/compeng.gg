from social_core.backends.discord import DiscordOAuth2
from social_core.backends.gitlab import GitLabOAuth2

class LaForgeBackend(GitLabOAuth2):
    name = 'laforge'
    API_URL = "https://laforge.eecg.utoronto.ca"

class CustomDiscordOAuth2(DiscordOAuth2):
    STATE_PARAMETER = False
