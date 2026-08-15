# Testing

Activate the development virtual environment, then run tests from `src/` with the dedicated test settings:

```bash
source ../venv/dev/bin/activate
APP_RUNMODE=dev DJANGO_SETTINGS_MODULE=ultimate.settings.test python manage.py test
```

The test settings use an in-memory SQLite database, disable external Google Apps credentials, and use a fast password hasher.

Pass a dotted test path to run a focused test:

```bash
APP_RUNMODE=dev DJANGO_SETTINGS_MODULE=ultimate.settings.test python manage.py test ultimate.leagues.tests
```
