from social_core.utils import get_strategy

from social_django.strategy import DjangoStrategy
from social_django.utils import STRATEGY, STORAGE

def load_strategy(validated_data=None):
    return get_strategy(STRATEGY, STORAGE, validated_data=validated_data)

class StatelessDjangoStrategy(DjangoStrategy):

    def __init__(self, storage, validated_data=None, request=None):
        super().__init__(storage, request)
        self.validated_data = validated_data

    # Request

    def request_data(self):
        return self.validated_data

    def request_host(self):
        """Return current host value"""
        raise NotImplementedError("'request_host' not implemented")

    def build_absolute_uri(self, path=None):
        return path

    # Session

    def session_get(self, name):
        raise NotImplementedError("'session_get' not implemented")

    def session_set(self, name, value):
        raise NotImplementedError("'session_set' not implemented")

    def session_pop(self, name):
        raise NotImplementedError("'session_pop' not implemented")
    
    # Responses

    def html(self, content):
        raise NotImplementedError("'html' not implemented")

    def redirect(self, url):
        raise NotImplementedError("'redirect' not implemented")

    def render_html(self, tpl=None, html=None, context=None):
        raise NotImplementedError("'render_html' not implemented")
