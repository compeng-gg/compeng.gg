from social_core.backends.gitlab import GitLabOAuth2

class LaForgeBackend(GitLabOAuth2):
    name = 'laforge'
    API_URL = "https://laforge.eecg.utoronto.ca"
