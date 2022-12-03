import environ

from .base import *

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

ENVIRONMENT = 'dev'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

INSTALLED_APPS += (
    'debug_toolbar',
    'django_extensions',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CAPTCHA_TEST_MODE = True

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_COLLAPSED': True,
}
