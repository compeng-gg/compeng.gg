import datetime
import json
import os
import pathlib

PROJECT_DIR = pathlib.Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR.parent
BUILTIN_FRONTEND = json.loads(os.environ.setdefault('BUILTIN_FRONTEND', 'true'))

# Core

APPEND_SLASH = True
ALLOWED_HOSTS = json.loads(os.environ.setdefault('ALLOWED_HOSTS', '[]'))
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

# Email
EMAIL_HOST = os.environ.setdefault('EMAIL_HOST', 'localhost')
EMAIL_PORT = json.loads(os.environ.setdefault('EMAIL_PORT', '465'))
EMAIL_HOST_USER = os.environ.setdefault('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.setdefault('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_SSL = json.loads(os.environ.setdefault('EMAIL_USE_SSL', 'true'))
DEFAULT_FROM_EMAIL = os.environ.setdefault('DEFAULT_FROM_EMAIL', '')
SERVER_EMAIL = os.environ.setdefault('SERVER_EMAIL', '')
ADMINS = json.loads(os.environ.setdefault('ADMINS', '[]'))

## Globalization (i18n/l10n)

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

## HTTP

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]
WSGI_APPLICATION = 'compeng_gg.wsgi.application'

## Models

INSTALLED_APPS = [
    'api',

    'courses',

    'discord_app',
    'github_app',
    'quercus_app',
    'youtube_app',

    'runner',

    'compeng_gg.django.github',

    'corsheaders',
    'social_django',
    'rest_framework',
    'rest_framework_simplejwt',

    'django.contrib.auth',
    'django.contrib.contenttypes',
]

## Security
CSRF_TRUSTED_ORIGINS = json.loads(os.environ.setdefault("CSRF_TRUSTED_ORIGINS",
    "[]"
))
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
                # 'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

## URLs

ROOT_URLCONF = 'compeng_gg.urls'

# Auth (django.contrib.auth)

AUTHENTICATION_BACKENDS = [
    'compeng_gg.auth.backends.CustomDiscordOAuth2',
    'compeng_gg.auth.backends.CustomGithubOAuth2',
    'compeng_gg.auth.backends.CustomGoogleOAuth2',
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

# Django CORS Headers (corsheaders)

CORS_ALLOWED_ORIGINS = json.loads(os.environ.setdefault('CORS_ALLOWED_ORIGINS',
    '["http://localhost:3000"]'
))
CORS_ALLOW_CREDENTIALS = False

# Social Auth (social_django)

SOCIAL_AUTH_STRATEGY = 'compeng_gg.auth.strategy.StatelessDjangoStrategy'
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
SOCIAL_AUTH_GITHUB_KEY = os.environ.setdefault('SOCIAL_AUTH_GITHUB_KEY',
    ''
)
SOCIAL_AUTH_GITHUB_SECRET = os.environ.setdefault('SOCIAL_AUTH_GITHUB_SECRET',
    ''
)
SOCIAL_AUTH_GOOGLE_KEY = os.environ.setdefault('SOCIAL_AUTH_GOOGLE_KEY',
    ''
)
SOCIAL_AUTH_GOOGLE_SECRET = os.environ.setdefault('SOCIAL_AUTH_GOOGLE_SECRET',
    ''
)
SOCIAL_AUTH_LAFORGE_KEY = os.environ.setdefault('SOCIAL_AUTH_LAFORGE_KEY',
    ''
)
SOCIAL_AUTH_LAFORGE_SECRET = os.environ.setdefault('SOCIAL_AUTH_LAFORGE_SECRET',
    ''
)
SOCIAL_AUTH_LAFORGE_SCOPE = [
    'read_user',
]
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'compeng_gg.auth.pipeline.associate_by_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'compeng_gg.auth.pipeline.laforge_user_details',
)
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['first_name', 'last_name']

# Django REST Framework (rest_framework)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
}

# Django REST Framework Simple JWT (rest_framework_simplejwt)

SIMPLE_JWT = {
    #"ACCESS_TOKEN_LIFETIME": datetime.timedelta(minutes=5),
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(days=1),
    # "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=30),
}

# Discord (discord)

DISCORD_BOT_TOKEN = os.environ.setdefault('DISCORD_BOT_TOKEN', '')
DISCORD_GUILD_ID = os.environ.setdefault('DISCORD_GUILD_ID', '')

# GitHub (github)

GITHUB_CONTENT_DIR = BASE_DIR / 'github_content'
GITHUB_ORGANIZATION = os.environ.setdefault('GITHUB_ORGANIZATION', '')
GITHUB_PRIVATE_KEY_B64 = os.environ.setdefault('GITHUB_PRIVATE_KEY_B64', '')
GITHUB_WEBHOOK_TOKEN = os.environ.setdefault('GITHUB_WEBHOOK_TOKEN', '')

# TODO: init this from environment
RUN_LOCALLY = True

## New GitHub module
GITHUB_WEBHOOK_SECRET = GITHUB_WEBHOOK_TOKEN # New name
GITHUB_API_URL = "https://api.github.com"

# Runner

RUNNER_QUEUE_HOST = os.environ.setdefault('RUNNER_QUEUE_HOST', 'localhost')
RUNNER_QUEUE_PORT = int(os.environ.setdefault('RUNNER_QUEUE_PORT', '8002'))
RUNNER_HOSTS = json.loads(os.getenv('RUNNER_HOSTS', '["localhost"]'))
RUNNER_USE_K8S = json.loads(os.environ.setdefault('RUNNER_USE_K8S', 'false'))

# Custom

AUTH_REDIRECT_URI = os.environ.setdefault(
    'AUTH_REDIRECT_URI', 'http://localhost:3000/auth/'
)

# Builtin Frontend

if BUILTIN_FRONTEND:
    INSTALLED_APPS += [
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
    ]
    TEMPLATES[0]['OPTIONS']['context_processors'] += [
        'django.contrib.messages.context_processors.messages',
    ]
    MIDDLEWARE += [
        'django.contrib.sessions.middleware.SessionMiddleware',
        # 'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ]
    STATIC_URL = '/api/static/'
    STATIC_ROOT = os.environ.setdefault("STATIC_ROOT", str(BASE_DIR / 'static'))
