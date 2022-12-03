import environ
import os
import sys

PROJECT_ROOT = os.path.dirname(__file__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    INTERNAL_IPS=(list, []),
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Django settings for ultimate-league-app project.

DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')
INTERNAL_IPS = env('INTERNAL_IPS')

ADMINS = (
    ('Ann Arbor Ultimate', 'web@annarborultimate.org'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
      'ENGINE': env('DB_ENGINE'),
      'NAME': env('DB_NAME'),
      'USER': env('DB_USER'),
      'PASSWORD': env('DB_PASSWORD'),
      'HOST': env('DB_HOST'),
      'PORT': env('DB_PORT'),
    }
}

TIME_ZONE = 'America/Detroit'
LANGUAGE_CODE = 'en-us'

USE_I18N = True
USE_L10N = True
USE_TZ = False

MEDIA_ROOT = os.path.join(BASE_DIR, '../media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, '../static/dist')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
      os.path.join(BASE_DIR, '../static/build'),
)

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': '',
        'STATS_FILE': os.path.join(STATIC_ROOT, '../build/stats.json'),
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = env('SECRET_KEY')

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'ultimate.middleware.error.ErrorUserMiddleware',
    'ultimate.middleware.http.Http403Middleware',
)

ROOT_URLCONF = 'ultimate.urls'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'anymail',
    'captcha',
    'compat',
    'hijack',
    'hijack_admin',
    'markdown_deux',
    'paypal.standard.ipn',
    'pytils',
    'webpack_loader',

    'ultimate',
    'ultimate.captain',
    'ultimate.index',
    'ultimate.junta',
    'ultimate.leagues',
    'ultimate.user',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',

                'ultimate.context_processors.google_analytics',
                'ultimate.context_processors.menu_leagues',
                'ultimate.context_processors.menu_items_home_sidebar',
                'ultimate.context_processors.menu_items_nav',
                'ultimate.context_processors.social_links',
            ],
        },
    },
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'a2u.email_groups': {
            'handlers': ['console',],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


# A2U
A2U_RATING_EXPIRATION_MONTHS = env('A2U_RATING_EXPIRATION_MONTHS')
A2U_RATING_LIMIT_MONTHS = env('A2U_RATING_LIMIT_MONTHS')


# USER
AUTH_USER_MODEL = 'user.User'
LOGIN_URL = '/user/log-in/'
LOGIN_REDIRECT_URL = '/user/'


# CAPTCHA
CAPTCHA_FONT_SIZE = 32
CAPTCHA_IMAGE_SIZE = (100, 36)
CAPTCHA_LETTER_ROTATION = None
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'


# GOOGLE APPS API
GOOGLE_APPS_API_ACCOUNT = ''
GOOGLE_APPS_API_CREDENTIALS_FILE = os.path.join(PROJECT_ROOT, '../../../config/', 'CREDENTIAL_FILE')
GOOGLE_APPS_API_SCOPES = (
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/admin.directory.group',
)
GOOGLE_APPS_CALENDAR_ID = env('GOOGLE_APPS_CALENDAR_ID')


# Annoucements Email Group/List Address
ANNOUNCEMENTS_GROUP_ADDRESS = env('ANNOUNCEMENTS_GROUP_ADDRESS')


# Hijack
HIJACK_ALLOW_GET_REQUESTS = True
HIJACK_REGISTER_ADMIN = False


# Markdown
MARKDOWN_DEUX_STYLES = {
    'default': {
        'extras': {
            'header-ids': True,
            'target-blank-links': True,
        },
        'safe_mode': False,
    },
}

# Email
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
EMAIL_BACKEND = 'anymail.backends.postmark.EmailBackend'
ANYMAIL = {
    'POSTMARK_SERVER_TOKEN': env('POSTMARK_SERVER_TOKEN'),
    'SEND_DEFAULTS': {
        'reply_to': [env('SEND_DEFAULTS_REPLY_TO')]
    }
}

# Paypal Info
PAYPAL_TEST = env('PAYPAL_TEST')
PAYPAL_BUY_BUTTON_IMAGE = STATIC_URL + 'static/images/paypal_checkout.png'
PAYPAL_SUBSCRIPTION_BUTTON_IMAGE = STATIC_URL + 'static/images/paypal_checkout.png'
PAYPAL_DONATION_BUTTON_IMAGE = STATIC_URL + 'static/images/paypal_checkout.png'
PAYPAL_BUSINESS_EMAIL = env('PAYPAL_BUSINESS_EMAIL')
