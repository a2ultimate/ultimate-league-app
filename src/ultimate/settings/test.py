"""Settings for running the test suite.

Builds on the dev settings but swaps in an in-memory SQLite database so the
suite runs anywhere without a live MySQL server, and blanks out the Google
Apps credentials file so GoogleAppsApi() can be constructed without real
service-account keys (tests mock the API surface).

Run with:
    APP_RUNMODE=dev DJANGO_SETTINGS_MODULE=ultimate.settings.test \
        python manage.py test
"""

from .dev import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# No real service-account keyfile in test/CI; GoogleAppsApi.__init__ skips
# credential loading when this is falsy, leaving self.http = None.
GOOGLE_APPS_API_CREDENTIALS_FILE = ""

# Fast, deterministic password hashing for tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Quiet the a2u.email_groups debug chatter during test runs.
import logging  # noqa: E402

logging.disable(logging.CRITICAL)
