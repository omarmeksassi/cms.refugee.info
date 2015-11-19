import os

gettext = lambda s: s
DATA_DIR = os.path.dirname(os.path.dirname(__file__))
"""
Django settings for cms_refugeeinfo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fkura$#8!926!quc%_ebwbk_t&*orvg3a&)+07vnl0vs^1c9@w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = TEMPLATE_DEBUG = 'DATABASE_URL' not in os.environ

ALLOWED_HOSTS = []


# Application definition





ROOT_URLCONF = 'cms_refugeeinfo.urls'

WSGI_APPLICATION = 'cms_refugeeinfo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases



# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'Europe/Athens'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/


STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'cms_refugeeinfo', 'static'),
)
SITE_ID = 1

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.csrf',
    'django.core.context_processors.tz',
    'sekizai.context_processors.sekizai',
    'django.core.context_processors.static',
    'cms.context_processors.cms_settings'
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'cms_refugeeinfo', 'templates'),
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'cms_refugeeinfo.basic_auth.BasicAuthMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware'
)

INSTALLED_APPS = (
    'storages',

    'djangocms_admin_style',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'cms',
    'menus',
    'sekizai',
    'treebeard',
    'djangocms_text_ckeditor',
    'djangocms_style',
    'djangocms_column',
    'djangocms_file',
    'djangocms_flash',
    'djangocms_googlemap',
    'djangocms_inherit',
    'djangocms_link',
    'djangocms_picture',
    'djangocms_teaser',
    'djangocms_video',
    'reversion',
    'cms_refugeeinfo',

    'title_plugin',
    'content_management',
)

LANGUAGES = (
    # # Customize this
    ('en', gettext('English')),
    ('ar', gettext('Arabic')),
    ('fa', gettext('Farsi')),
    ('af', gettext('Pashto')),
    ('el', gettext('Greek')),
)

CMS_LANGUAGES = {
    # # Customize this
    'default': {
        'public': True,
        'hide_untranslated': False,
        'redirect_on_fallback': True,
    },
    1: [
        {
            'public': True,
            'code': 'en',
            'hide_untranslated': False,
            'name': gettext('en'),
            'redirect_on_fallback': True,
        },
        {
            'public': True,
            'code': 'ar',
            'hide_untranslated': False,
            'name': gettext('ar'),
            'redirect_on_fallback': True,
        },
        {
            'public': True,
            'code': 'fa',
            'hide_untranslated': False,
            'name': gettext('fa'),
            'redirect_on_fallback': True,
        },
        {
            'public': True,
            'code': 'af',
            'hide_untranslated': False,
            'name': gettext('Pashto'),
            'redirect_on_fallback': True,
        },
        {
            'public': True,
            'code': 'el',
            'hide_untranslated': False,
            'name': gettext('el'),
            'redirect_on_fallback': True,
        },
    ],
}

CMS_TEMPLATES = (
    # # Customize this
    ('fullwidth.html', 'Fullwidth'),
)

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF = {}

CKEDITOR_SETTINGS = {
    'language': '{{ language }}',
    'toolbar_CMS': [
        ['Undo', 'Redo'],
        ['cmsplugins', '-', 'ShowBlocks'],
        ['Format', 'Styles'],
        ['TextColor', 'BGColor', '-', 'PasteText', 'PasteFromWord'],
        ['Maximize', ''],
        '/',
        ['Bold', 'Italic', 'Underline', '-', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
        ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'BidiLtr','BidiRtl'],
        ['HorizontalRule'],
        ['Link', 'Unlink', 'Anchor'],
        ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Table'],
        ['Source']
    ],
    'skin': 'moono',
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'HOST': 'localhost',
        'NAME': 'project.db',
        'PASSWORD': '',
        'PORT': '',
        'USER': ''
    }
}

MIGRATION_MODULES = {
    'djangocms_flash': 'djangocms_flash.migrations_django',
    'djangocms_file': 'djangocms_file.migrations_django',
    'djangocms_inherit': 'djangocms_inherit.migrations_django',
    'djangocms_column': 'djangocms_column.migrations_django',
    'djangocms_video': 'djangocms_video.migrations_django',
    'djangocms_picture': 'djangocms_picture.migrations_django',
    'djangocms_googlemap': 'djangocms_googlemap.migrations_django',
    'djangocms_style': 'djangocms_style.migrations_django',
    'djangocms_teaser': 'djangocms_teaser.migrations_django'
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Amazon S3 credentials
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Amazon S3 URL
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

# Static files location
STATICFILES_STORAGE = 'cms_refugeeinfo.custom_storages.StaticFilesStorage'

# Default File storage
MEDIAFILES_LOCATION = 'media'
STATICFILES_LOCATION = 'static'


#Transifex Creds
TRANSIFEX_USER = os.environ.get('TRANSIFEX_USER')
TRANSIFEX_PASSWORD = os.environ.get('TRANSIFEX_PASSWORD')
TRANSIFEX_PROJECT_SLUG = os.environ.get('TRANSIFEX_PROJECT_SLUG')

MEDIA_URL = "https://dttv0ybwk2jfe.cloudfront.net/%s/" % ( MEDIAFILES_LOCATION,)
STATIC_URL = 'https://dttv0ybwk2jfe.cloudfront.net/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

DEFAULT_FILE_STORAGE = 'cms_refugeeinfo.custom_storages.MediaFilesStorage'

ALLOWED_HOSTS = ['*']

import dj_database_url

DJ_URL = dj_database_url.config()
if 'ENGINE' in DJ_URL:
    DATABASES['default'] = DJ_URL

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARN'),
        },
    },
}

CMS_PUBLIC_FOR = 'staff'
#DEBUG = False