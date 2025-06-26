"""
Base settings for VITAL MASTERY project.
"""

import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

# Read .env file from the project root
environ.Env.read_env(os.path.join(BASE_DIR.parent, 'env.example'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Application definition
DJANGO_APPS = [
    'daphne',  # Must be first for ASGI support
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'django_eventstream',
    'rest_framework',
    'corsheaders',
    'parler',
    'django_prose_editor',
]

LOCAL_APPS = [
    'apps.users',
    'apps.content',
    'apps.interactions',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vital_mastery.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'js_asset.context_processors.importmap',  # Required for Django-Prose-Editor
            ],
        },
    },
]

WSGI_APPLICATION = 'vital_mastery.wsgi.application'
ASGI_APPLICATION = 'vital_mastery.asgi.application'

# Database
DATABASES = {
    'default': env.db()
}

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Password validation
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

# Internationalization
LANGUAGE_CODE = env('LANGUAGE_CODE', default='th')
TIME_ZONE = env('TIME_ZONE', default='Asia/Bangkok')
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Languages supported
LANGUAGES = [
    ('en', 'English'),
    ('th', 'Thai'),
]

# Parler configuration for multilingual content
PARLER_LANGUAGES = {
    None: (
        {'code': 'th'},
        {'code': 'en'},
    ),
    'default': {
        'fallbacks': ['th'],
        'hide_untranslated': False,
    }
}

# Static files (CSS, JavaScript, Images) - Django 5.0.3 compatible
STATIC_URL = env('STATIC_URL', default='/static/')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Django 5.0.3 STORAGES configuration
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media files
MEDIA_URL = env('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# CORS settings
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True

# Django-Prose-Editor Configuration
# The editor is configured directly in model fields and admin forms
# No global configuration is required for basic usage

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Django-EventStream Configuration
EVENTSTREAM_STORAGE_CLASS = 'django_eventstream.storage.DjangoModelStorage'

# Redis Configuration for real-time features
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

# EventStream Configuration with Redis for scaling
EVENTSTREAM_REDIS = {
    'host': env('REDIS_HOST', default='localhost'),
    'port': env('REDIS_PORT', default=6379),
    'db': env('REDIS_DB', default=0),
}

# Cache configuration for Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'vital_mastery',
        'TIMEOUT': 300,  # 5 minutes default timeout
    }
}

# Channel layer configuration for real-time features
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
            'capacity': 1500,
            'expiry': 60,
        },
    },
}

# Rate limiting configuration
RATELIMIT_STORAGE = 'default'
RATELIMIT_USE_CACHE = 'default'

# SSE Authentication and Security
SSE_ALLOWED_ORIGINS = env.list('SSE_ALLOWED_ORIGINS', default=CORS_ALLOWED_ORIGINS)
SSE_MAX_CONNECTIONS_PER_USER = env.int('SSE_MAX_CONNECTIONS_PER_USER', default=5)
SSE_CONNECTION_TIMEOUT = env.int('SSE_CONNECTION_TIMEOUT', default=3600)  # 1 hour

# Real-time feature configuration
REALTIME_SETTINGS = {
    'ENABLE_COLLABORATIVE_EDITING': env.bool('ENABLE_COLLABORATIVE_EDITING', default=True),
    'EDITING_SESSION_TIMEOUT': env.int('EDITING_SESSION_TIMEOUT', default=300),  # 5 minutes
    'HEARTBEAT_INTERVAL': env.int('HEARTBEAT_INTERVAL', default=30),  # 30 seconds
    'MAX_EDITING_SESSIONS_PER_ARTICLE': env.int('MAX_EDITING_SESSIONS_PER_ARTICLE', default=10),
    'COUNTER_CACHE_TIMEOUT': env.int('COUNTER_CACHE_TIMEOUT', default=60),  # 1 minute
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django_eventstream': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
} 