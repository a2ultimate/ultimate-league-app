"""System-integrity smoke tests.

Two cheap but high-signal guards for the upgrade:

* ``check --deploy``-free system checks must pass (deprecated settings, bad admin
  config, and removed-feature usage surface here as the Django version climbs).
* The models and the migration graph must agree -- no field change (e.g. adding
  ``on_delete`` or ``DEFAULT_AUTO_FIELD`` shifts) should leave an un-generated
  migration behind. ``makemigrations --check`` fails the run if one is missing.
"""

from io import StringIO

from django.core.management import call_command
from django.core.management.base import SystemCheckError
from django.template import engines
from django.test import TestCase


class SystemCheckTest(TestCase):
    def test_system_checks_pass(self):
        try:
            call_command("check")
        except SystemCheckError as exc:  # pragma: no cover - failure path
            self.fail("manage.py check reported issues:\n{}".format(exc))

    def test_no_missing_migrations(self):
        out = StringIO()
        try:
            call_command("makemigrations", "--check", "--dry-run", stdout=out, stderr=out)
        except SystemExit as exc:
            # --check exits non-zero when migrations are missing.
            self.fail(
                "Missing migrations detected by makemigrations --check:\n{}".format(out.getvalue())
            )


class WebpackLoaderTest(TestCase):
    """Guard the django-webpack-loader integration.

    The loader's config format and stats.json contract changed across major
    versions (3.x needs a CACHE key and a different stats shape than the build
    emits). This renders a real bundle against the committed stats.json so a
    silently-incompatible webpack-loader version fails the suite instead of
    rendering empty markup at runtime.
    """

    def _render(self, kind):
        t = engines["django"].from_string(
            '{% load render_bundle from webpack_loader %}'
            '{% render_bundle "main" "' + kind + '" %}'
        )
        return t.render({})

    def test_js_bundle_resolves_from_stats(self):
        # The committed stats.json's "main" chunk carries a JS asset; the loader
        # must turn it into a <script> tag (proves get_bundle works end-to-end).
        out = self._render("js")
        self.assertIn("<script", out)
        self.assertIn("main-", out)
