"""
Django settings for wpcsite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/

Designed for Heroku and http://12factor.net/config.  Configuration is
overriden by environment variables.

One way to set environment variables for local development in a virtualenv:

$ vi $VIRTUAL_ENV/bin/postactivate
export DJANGO_DEBUG=1
$ vi $VIRTUAL_ENV/bin/predeactivate
unset DJANGO_DEBUG
$ source $VIRTUAL_ENV/bin/postactivate

A second way to to use an .env file.  See env.dist.

To set environment variables in heroku environment
$ heroku config
$ heroku config:set DJANGO_DEBUG=1

Environment variables:
ADMIN_NAMES, ADMIN_EMAILS - comma-separted list of names and emails of admins
ALLOWED_HOSTS - comma-separated list of allowed hosts
BROKER_URL - Broker URL string for Celery
CELERY_ALWAYS_EAGER - 1 to run all tasks synchronosly. Defaults to 1 if
    BROKER_URL is undefined, or 0 if defined
CELERY_RESULT_BACKEND - Backend URL string for Celery
CSRF_COOKIE_HTTPONLY - Prevent in-page JS from accessing CSRF token
CSRF_COOKIE_SECURE - Only send CSRF cookies on HTTPS connections
DATABASE_URL - See https://github.com/kennethreitz/dj-database-url
DEFAULT_FROM_EMAIL - "From" email for emails to users
DJANGO_DEBUG - 1 to enable, 0 to disable, default disabled
DRF_INSTANCE_CACHE_POPULATE_COLD - 1 to recursively populate a cold cache on
    updates, 0 to be eventually consistent, default enabled
EMAIL_BACKEND - The backend for email services
EMAIL_FILE_PATH - File path when FileSystemStorage is used
EMAIL_HOST - SMTP server, default localhost
EMAIL_HOST_PASSWORD - SMTP server password, default none
EMAIL_HOST_USER - SMTP server username, default none
EMAIL_PORT - SMTP server ports, default 25
EMAIL_SUBJECT_PREFIX - Prefix for subject line of emails to admins
EMAIL_USE_SSL - 1 to use SSL SMTP connection, usually on port 465
EMAIL_USE_TLS - 1 to use TLS SMTP connection, usually on port 587
EXTRA_INSTALLED_APPS - comma-separated list of apps to add to INSTALLED_APPS
FXA_OAUTH_ENDPOINT - Override for Firefox Account OAuth2 endpoint
FXA_PROFILE_ENDPOINT - Override for Firefox Account profile endpoint
FXA_SCOPE - Override default OAuth2 scope
MDN_ALLOWED_URL_PREFIXES - comma-separated list of URL prefixes allowed by
    the scraper
MDN_SHOW_REPARSE - 1 to show Reparse button, defaults to DEBUG
MEMCACHE_SERVERS - semicolon-separated list of memcache servers
MEMCACHE_USERNAME - username for memcache servers
MEMCACHE_PASSWORD - password for memcache servers
PAGE_SIZE - Items per page, default 10
REDIS_URL - Redis URL string to use Redis for caching
SECRET_KEY - Overrides SECRET_KEY
SECURE_BROWSER_XSS_FILTER - Enable browser-based XSS protection
SECURE_CONTENT_TYPE_NOSNIFF - Add nosniff header to disallow browser guessing
SECURE_HSTS_INCLUDE_SUBDOMAINS - Strict Transport Security for subdomains
SECURE_HSTS_SECONDS - Number of seconds for Strict Transport Security header,
    0 to disable (default)
SECURE_PROXY_SSL_HEADER - 'HTTP_X_FORWARDED_PROTOCOL,https' to enable
SECURE_SSL_REDIRECT - 301 Redirect http:// to https://
SERVER_EMAIL - Email "From" address for error messages to admins
SESSION_COOKIE_SECURE - Only send session cookies on HTTPS connections
STATIC_ROOT - Overrides STATIC_ROOT
USE_DRF_INSTANCE_CACHE - 1 to enable, 0 to disable, default enabled
USE_CACHE - 1 to enable, 0 to disable, default enabled
X_FRAME_OPTIONS - Set X-Frame-Options value
"""
from os import path
import sys

from decouple import config, Csv
from dj_database_url import parse as db_url

BASE_DIR = path.dirname(path.dirname(__file__))


def rel_path(*subpaths):
    """Convert a list of relative paths to an absolute path."""
    return path.join(BASE_DIR, *subpaths)


cast_list = Csv()  # Convert comma-separated strings to lists

# Detect that we're running tests
TESTING = sys.argv[1:2] == ['test']

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    'SECRET_KEY',
    default='jl^8zustdy8ht@=abml-j@%hp7hr-0u-41hb*1=duc91a%=9+%')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

# Security settings
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=cast_list)
SECURE_PROXY_SSL_HEADER = config(
    'SECURE_PROXY_SSL_HEADER', default='', cast=cast_list) or None
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
    'SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config(
    'SECURE_CONTENT_TYPE_NOSNIFF', default=False, cast=bool)
SECURE_BROWSER_XSS_FILTER = config(
    'SECURE_BROWSER_XSS_FILTER', default=False, cast=bool)
SECURE_SSL_REDIRECT = config(
    'SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_SSL_HOST = config(
    'SECURE_SSL_HOST', default='', cast=cast_list) or None
SECURE_REDIRECT_EXCEMPT = config(
    'SECURE_REDIRECT_EXCEMPT', default='', cast=cast_list)
SESSION_COOKIE_SECURE = config(
    'SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_HTTPONLY = config(
    'CSRF_COOKIE_HTTPONLY', default=False, cast=bool)
CSRF_COOKIE_SECURE = config(
    'CSRF_COOKIE_SECURE', default=False, cast=bool)
X_FRAME_OPTIONS = config('X_FRAME_OPTIONS', default='SAMEORIGIN')

AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.fxa',
    'corsheaders',
    'django_extensions',
    'django_jinja',
    'django_nose',
    'mptt',
    'oauth2_provider',
    'simple_history',
    'rest_framework',
    'puente',

    'bcauth',
    'mdn',
    'webplatformcompat',
]
INSTALLED_APPS.extend(
    config('EXTRA_INSTALLED_APPS', default='', cast=cast_list))

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'webplatformcompat.history.HistoryChangesetMiddleware',
)

ROOT_URLCONF = 'wpcsite.urls'

WSGI_APPLICATION = 'wpcsite.wsgi.application'

# django-allauth requires some settings
SITE_ID = config('SITE_ID', default='1', cast=int)

# Email settings
ADMINS = zip(
    config('ADMIN_NAMES', default='', cast=cast_list),
    config('ADMIN_EMAILS', default='', cast=cast_list))
EMAIL_BACKEND = config(
    'EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_SUBJECT_PREFIX = config('EMAIL_SUBJECT_PREFIX', default='[Django] ')
SERVER_EMAIL = config('SERVER_EMAIL', default='root@localhost')
DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL', default='webmaster@localhost')
_email_file_path = config('EMAIL_FILE_PATH', default='')
if _email_file_path:
    EMAIL_FILE_PATH = _email_file_path


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='sqlite:///' + rel_path('db.sqlite3'),
        cast=db_url)
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Templates
_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.template.context_processors.debug',
    'django.template.context_processors.i18n',
    'django.template.context_processors.media',
    'django.template.context_processors.static',
    'django.template.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
]
TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            # Use jinja2/ for jinja templates
            'app_dirname': 'jinja2',
            # Don't figure out which template loader to use based on file
            # extension
            'match_extension': '',
            'newstyle_gettext': True,
            'trim_blocks': True,
            'context_processors': _CONTEXT_PROCESSORS,
            'extensions': [
                'django_jinja.builtins.extensions.CsrfExtension',
                'jinja2.ext.autoescape',
                'puente.ext.i18n',
                'wpcsite.jinja2.WPCExtension',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            rel_path('bcauth', 'templates'),
            rel_path('webplatformcompat', 'templates'),
        ),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': _CONTEXT_PROCESSORS,
        }
    },
]

# L10n extraction configuration
PUENTE = {
    'BASE_DIR': BASE_DIR,
    'DOMAIN_METHODS': {
        'django': [
            ('**/migrations/**', 'ignore'),

            ('bcauth/**.py', 'python'),
            ('bcauth/**/jinja2/**.html', 'jinja2'),

            ('mdn/**.py', 'python'),
            ('mdn/**/jinja2/**.html', 'jinja2'),

            ('webplatformcompat/**.py', 'python'),
            ('webplatformcompat/**/jinja2/**.html', 'jinja2'),

            # FIXME: This doesn't pull in strings from libraries including
            # email templates in django-allauth.
        ]
    },
    'PROJECT': 'BrowserCompat',
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = config('STATIC_ROOT', default='') or None
STATIC_URL = '/static/'

#
# Caching
#
# In Heroku, use MemCachier and load from environment
# https://devcenter.heroku.com/articles/django-memcache
# Otherwise, use django-pylibmc environment variables or locmen
# https://github.com/jbalogh/django-pylibmc
# TODO: see if standard django.core.cache.backends.memcached.PyLibMCCache
#  can be configured to work with MemCachier, or switch to Redis

_memcachier_servers = config(
    'MEMCACHIER_SERVERS', default='').replace(',', ';')
_memcache_servers = config('MEMCACHE_SERVERS', default=_memcachier_servers)
_redis_url = config('REDIS_URL', default='')
_use_cache = config('USE_CACHE', default=True, cast=bool) and not TESTING

if _memcache_servers and _use_cache:
    _memcachier_username = config('MEMCACHIER_USERNAME', default='')
    _memcachier_password = config('MEMCACHIER_PASSWORD', default='')
    _memcache_username = config(
        'MEMCACHE_USERNAME', default=_memcachier_username)
    _memcache_password = config(
        'MEMCACHE_PASSWORD', default=_memcachier_password)

    # Set environment variables because that's what django_pylibmc needs.
    from os import environ
    environ['MEMCACHE_SERVERS'] = _memcache_servers
    environ['MEMCACHE_USERNAME'] = _memcache_username
    environ['MEMCACHE_PASSWORD'] = _memcache_password

    # Use memcache
    CACHES = {
        'default': {
            'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
            'TIMEOUT': 500,
            'BINARY': True,
            'OPTIONS': {
                'no_block': True,
                'tcp_nodelay': True,
                'tcp_keepalive': True,
                'remove_failed': 4,
                'retry_timeout': 2,
                'dead_timeout': 10,
                '_poll_timeout': 2000,
            },
        },
    }
elif _redis_url and _use_cache:
    # Use redis
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': _redis_url,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient'
            }
        }
    }
else:
    # Use local cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
    }
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# When the number of descendants means to paginate a view_feature
PAGINATE_VIEW_FEATURE = 50

# Authentication
LOGIN_URL = '/accounts/login/'

# MDN Scraping
if TESTING:
    MDN_ALLOWED_URLS = ('https://developer.mozilla.org/en-US/', )
else:
    MDN_ALLOWED_URLS = config(
        'MDN_ALLOWED_URL_PREFIXES',
        default='https://developer.mozilla.org/en-US/',
        cast=cast_list)
MDN_SHOW_REPARSE = config('MDN_SHOW_REPARSE', default=DEBUG, cast=bool)

#
# 3rd Party Libraries
#


# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'webplatformcompat.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'VIEW_NAME_FUNCTION': 'webplatformcompat.utils.get_view_name',
    'DEFAULT_PAGINATION_CLASS': 'webplatformcompat.pagination.Pagination',
    'PAGE_SIZE': config('PAGE_SIZE', default=10, cast=int),
    'DEFAULT_VERSIONING_CLASS': (
        'rest_framework.versioning.NamespaceVersioning'),
    'EXCEPTION_HANDLER': 'webplatformcompat.exceptions.handler',
}

# Django nose
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Django Debug Toolbar
if DEBUG:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        assert debug_toolbar
        INSTALLED_APPS.append('debug_toolbar')

# Celery - async task management
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

if TESTING:
    CELERY_ALWAYS_EAGER = True
else:
    _broker_url = config('BROKER_URL', default='')
    if _broker_url:
        BROKER_URL = _broker_url
        _eager_default = False
    else:
        _eager_default = True
    CELERY_ALWAYS_EAGER = config(
        'CELERY_ALWAYS_EAGER', default=_eager_default, cast=bool)
    _celery_result_backend = config('CELERY_RESULT_BACKEND', default='')
    if _celery_result_backend:
        CELERY_RESULT_BACKEND = _celery_result_backend

# DRF Cached Instances - avoid DB reads for Django REST Framework
USE_DRF_INSTANCE_CACHE = config(
    'USE_DRF_INSTANCE_CACHE', default=True, cast=bool)
DRF_INSTANCE_CACHE_POPULATE_COLD = config(
    'DRF_INSTANCE_CACHE_POPULATE_COLD', default=True, cast=bool)

# CORS Middleware
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# django-allauth
SOCIALACCOUNT_PROVIDERS = {
    'fxa': {
        'SCOPE': config(
            'FXA_SCOPE',
            default='profile:uid,profile:email',
            cast=cast_list),
        'OAUTH_ENDPOINT': config(
            'FXA_OAUTH_ENDPOINT',
            default='https://oauth.accounts.firefox.com/v1'),
        'PROFILE_ENDPOINT': config(
            'FXA_PROFILE_ENDPOINT',
            default='https://profile.accounts.firefox.com/v1'),
    }
}
