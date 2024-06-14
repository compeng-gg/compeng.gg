import datetime
import json
import os
import pathlib

PROJECT_DIR = pathlib.Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR.parent

# Core

APPEND_SLASH = True
ALLOWED_HOSTS = json.loads(os.getenv('ALLOWED_HOSTS', '[]'))
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

## Database

DATABASES = json.loads(os.environ.setdefault('DATABASES', json.dumps({
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / 'db.sqlite3'),
    }
})))

## Debugging

DEBUG = json.loads(os.environ.setdefault('DEBUG', 'true'))

## Globalization (i18n/l10n)

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

## HTTP

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]
WSGI_APPLICATION = 'compeng_gg.wsgi.application'

## Models

INSTALLED_APPS = [
    'api',

    'discord',

    'courses',

    'docs',
    'webhook',
    'lab5',

    'social_django',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',

    'corsheaders',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

## Security

CSRF_COOKIE_AGE = 31449600
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_COOKIE_PATH = '/'
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_TRUSTED_ORIGINS = json.loads(os.getenv('CSRF_TRUSTED_ORIGINS', '[]'))
CSRF_USE_SESSIONS = False
SECRET_KEY = os.environ.setdefault('SECRET_KEY',
    'django-insecure-i%y%&uud=jfqzakf!ee5+j12hv=q)r9v*(569c5%%gh9n2#7fg'
)

## Templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(PROJECT_DIR.joinpath("templates"))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

## URLs

ROOT_URLCONF = 'compeng_gg.urls'

# Auth (django.contrib.auth)

AUTHENTICATION_BACKENDS = [
    'social_core.backends.discord.DiscordOAuth2',
    'compeng_gg.auth.backends.LaForgeBackend',
    'django.contrib.auth.backends.ModelBackend',
]
LOGIN_REDIRECT_URL = 'login_redirect'
LOGIN_URL = 'login'
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Sessions (django.contrib.sessions)

SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_FILE_PATH = None
SESSION_SAVE_EVERY_REQUEST = False
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# Static Files (django.contrib.staticfiles)

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    str(PROJECT_DIR.joinpath("static")),
]

# Django CORS Headers (corsheaders)

CORS_ALLOWED_ORIGINS = json.loads(os.getenv('CORS_ALLOWED_ORIGINS', '[]'))
CORS_ALLOW_CREDENTIALS = False

# Social Auth (social_django)

SOCIAL_AUTH_URL_NAMESPACE = 'auth'
SOCIAL_AUTH_REQUIRE_POST = False

SOCIAL_AUTH_DISCORD_KEY = os.environ.setdefault('SOCIAL_AUTH_DISCORD_KEY',
    ''
)
SOCIAL_AUTH_DISCORD_SECRET = os.environ.setdefault('SOCIAL_AUTH_DISCORD_SECRET',
    ''
)
SOCIAL_AUTH_DISCORD_SCOPE = [
    'identify',
    'guilds.join',
]
SOCIAL_AUTH_LAFORGE_KEY = os.environ.setdefault('SOCIAL_AUTH_LAFORGE_KEY',
    ''
)
SOCIAL_AUTH_LAFORGE_SECRET = os.environ.setdefault('SOCIAL_AUTH_LAFORGE_SECRET',
    ''
)
SOCIAL_AUTH_LAFORGE_SCOPE = [
    "read_user",
    "read_repository",
]
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    'compeng_gg.auth.pipeline.disallow_new_discord',
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)

# Django REST Framework (rest_framework)

REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ]
}

# Django REST Framework Simple JWT (rest_framework_simplejwt)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=1),
}

# Discord (discord)

DISCORD_BOT_TOKEN = os.environ.setdefault('DISCORD_BOT_TOKEN', '')

# Webhook (webhook)

WEBHOOK_TOKEN = os.environ.setdefault('WEBHOOK_TOKEN', '')
WEBHOOK_HOSTS = json.loads(os.getenv("WEBHOOK_HOSTS", '["localhost"]'))
