import environ

from .base import *

env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(BASE_DIR), '.env'))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EMAIL_BACKEND = env('EMAIL_BACKEND')

MIDDLEWARE_CLASSES = (
    'bugsnag.django.middleware.BugsnagMiddleware',
) + MIDDLEWARE_CLASSES

# BUGSNAG
BUGSNAG = {
    'api_key': env('BUGSNAG_API_KEY'),
    'project_root': BASE_DIR,
}

# GOOGLE ANALYTICS
GOOGLE_ANALYTICS_MEASUREMENT_ID = env('GOOGLE_ANALYTICS_MEASUREMENT_ID')
