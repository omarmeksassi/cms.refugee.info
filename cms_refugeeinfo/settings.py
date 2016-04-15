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
DEBUG = 'DATABASE_URL' not in os.environ

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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
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
            ],
        },

    },
]

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
    'filer',
    'easy_thumbnails',
    'mptt',

    'audio_content',
    'survey_element',
    'border_closures',
    'title_plugin',
    'content_management',
    'project_management',
    'djcelery',
    'kombu.transport.django',
)

LANGUAGES = (
    # # Customize this
    ('en', gettext('English')),
    ('ar', gettext('Arabic')),
    ('fa', gettext('Farsi')),
    ('af', gettext('Pashto')),
    ('el', gettext('Greek')),
    # ('mk', gettext('Macedonian')),
    # ('rs', gettext('Serbian')),
    # ('de', gettext('German')),
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
            'name': gettext('English'),
            'redirect_on_fallback': True,
        },
        {
            'public': True,
            'code': 'ar',
            'hide_untranslated': False,
            'name': gettext('Arabic'),
            'redirect_on_fallback': True,
        },
        {
            'public': True,
            'code': 'fa',
            'hide_untranslated': False,
            'name': gettext('Farsi'),
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
            'name': gettext('Greek'),
            'redirect_on_fallback': True,
        },

        # {
        # 'public': True,
        # 'code': 'rs',
        #    'hide_untranslated': False,
        #    'name': gettext('Serbian'),
        #    'redirect_on_fallback': True,
        #},
        #{
        #    'public': True,
        #    'code': 'mk',
        #    'hide_untranslated': False,
        #    'name': gettext('Macedonian'),
        #    'redirect_on_fallback': True,
        #},
        #{
        #    'public': True,
        #    'code': 'de',
        #    'hide_untranslated': False,
        #    'name': gettext('German'),
        #    'redirect_on_fallback': True,
        #},
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
        ['ShowBlocks'],
        ['Format', 'Styles'],
        ['TextColor', 'BGColor', '-', 'PasteText', 'PasteFromWord'],
        ['Maximize', ''],
        '/',
        ['Bold', 'Italic', 'Underline', '-', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
        ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'BidiLtr', 'BidiRtl'],
        ['HorizontalRule'],
        ['Link', 'Unlink', 'Anchor', 'Image'],
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


# Default File storage
MEDIAFILES_LOCATION = 'media'
STATICFILES_LOCATION = 'static'


# Transifex Creds
TRANSIFEX_USER = os.environ.get('TRANSIFEX_USER')
TRANSIFEX_PASSWORD = os.environ.get('TRANSIFEX_PASSWORD')
TRANSIFEX_PROJECT_SLUG = os.environ.get('TRANSIFEX_PROJECT_SLUG')
TRANSIFEX_UPLOAD_ON_PUBLISH = os.environ.get('TRANSIFEX_UPLOAD_ON_PUBLISH', 'True') == 'True'

TRANSIFEX_PROJECTS = {
    'refugeeinfo': filter(None, os.environ.get('TRANSIFEX_PROJECTS_ALL', '').split(',')),
    'refugee-info-irc': filter(None, os.environ.get('TRANSIFEX_PROJECTS_IRC', '').split(','))
}

STATICFILES_STORAGE = 'cms_refugeeinfo.custom_storages.StaticFilesStorage'

MEDIA_URL = 'https://{}/{}/'.format(os.environ.get('CLOUDFRONT_DISTRIBUTION', 'd3w2ev2d100chk.cloudfront.net'),
                                    MEDIAFILES_LOCATION)
STATIC_URL = 'https://{}/'.format(os.environ.get('CLOUDFRONT_DISTRIBUTION', 'd3w2ev2d100chk.cloudfront.net'))
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

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

CMS_PUBLIC_FOR = 'staff'
# CELERY_ALWAYS_EAGER = True

# Jira workflow settings

JIRA_URL = os.environ.get('JIRA_URL', 'https://refugeeinfo.atlassian.net')
JIRA_USER = os.environ.get('JIRA_USER')
JIRA_PASSWORD = os.environ.get('JIRA_PASSWORD')
JIRA_PROJECT = os.environ.get('JIRA_PROJECT', "CM")
JIRA_ISSUE_TYPE = os.environ.get('JIRA_ISSUE_TYPE', "10003")
JIRA_PAGE_ADDRESS_FIELD = os.environ.get('JIRA_PAGE_ADDRESS_FIELD', 'customfield_10024')
JIRA_LANGUAGES = os.environ.get('JIRA_LANGUAGES', 'ar,fa')
JIRA_TRANSITIONS = {
    'translations-complete': os.environ.get('JIRA_TRANSITIONS_TRANSLATED', 81),
    'translations-reviewed': os.environ.get('JIRA_TRANSITIONS_REVIEWED', 91),
    're-edit': os.environ.get('JIRA_TRANSITIONS_REEDIT', 141),
    'validated': os.environ.get('JIRA_TRANSITIONS_VALIDATED', 71),
}


PREPROCESS_HTML = False if not 'PREPROCESS_HTML' in os.environ else os.environ.get('PREPROCESS_HTML').split(',')
