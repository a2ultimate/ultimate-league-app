"""Tests for the markdownify template filter.

This filter replaced the unmaintained django-markdown-deux during the Django
4.2 upgrade (markdown_deux imported force_unicode, removed in Django 4.0). It
now renders the markdown content on the static-page and news-article templates,
so pin down the two behaviors that matter: markdown is converted to HTML, and
raw HTML in the source is escaped (safe_mode) rather than passed through.
"""

from django.test import TestCase
from django.utils.safestring import SafeString

from ultimate.templatetags.md import markdownify


class MarkdownifyFilterTest(TestCase):
    def test_converts_markdown_to_html(self):
        out = markdownify("**bold**")
        self.assertIn("<strong>bold</strong>", out)

    def test_escapes_raw_html(self):
        out = markdownify("<script>alert(1)</script>")
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)

    def test_returns_safe_string(self):
        # mark_safe output prevents the template engine from double-escaping.
        self.assertIsInstance(markdownify("hi"), SafeString)

    def test_handles_empty_and_none(self):
        # The `text or ''` guard means None doesn't raise; both render to the
        # same (empty-ish) markup rather than blowing up.
        self.assertNotIn("None", markdownify(None))
        self.assertEqual(markdownify(""), markdownify(None))
