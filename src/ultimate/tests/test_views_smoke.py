"""View-rendering smoke tests across every app.

These don't assert business logic -- they assert that requesting each page does
not blow up (no 500). That is exactly the failure mode a Django version bump
introduces: a removed template tag, a moved import inside a view, a model field
API change, or broken middleware surfaces as a 500 on render. A green run here at
each upgrade hop means the request/response/template path still holds together.

Public pages must return 200. Login-required pages must redirect anonymous users
to the login URL (302), and render (non-5xx) for an authenticated user.
"""

from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ultimate.index.models import NewsArticle, StaticContent

User = get_user_model()


class PublicPageSmokeTest(TestCase):
    """Pages reachable without authentication should render with HTTP 200."""

    @classmethod
    def setUpTestData(cls):
        # Back the content-driven pages so the views find a row instead of 404.
        # Note the route name -> content_url mapping is not 1:1 (e.g. the
        # 'contact' route renders the 'contacts' StaticContent).
        for slug in ("about", "club", "contacts", "pickup", "rules", "welcome"):
            StaticContent.objects.create(
                url=slug, title=slug.title(), type="plain", content="hello"
            )
        StaticContent.objects.create(
            url="foo", title="Foo", type="markdown", content="# Foo"
        )
        # NewsArticle.save() is overridden without *args/**kwargs, so
        # objects.create() (which passes force_insert=) fails; build and save
        # the instance directly. published is required (no default); a past
        # date keeps it visible. USE_TZ is False, so use a naive datetime.
        cls.article = NewsArticle(
            title="An Article", type="plain", content="body",
            published=datetime(2020, 1, 1, 0, 0, 0),
        )
        cls.article.save()

    def assertOk(self, name, **kwargs):
        resp = self.client.get(reverse(name, kwargs=kwargs))
        self.assertEqual(resp.status_code, 200, "{} returned {}".format(name, resp.status_code))

    def test_home(self):
        self.assertOk("home")

    def test_announcements(self):
        self.assertOk("announcements")

    def test_static_menu_pages(self):
        for name in ("about", "club", "contact", "pickup", "rules", "welcome"):
            self.assertOk(name)

    def test_static_page_by_url(self):
        self.assertOk("static_page", content_url="foo")

    def test_news_article(self):
        self.assertOk("news_acticle", url=self.article.url)

    def test_login_page(self):
        self.assertOk("auth_log_in")

    def test_signup_page(self):
        self.assertOk("registration_register")


class LoginRequiredRedirectTest(TestCase):
    """Anonymous access to protected pages should redirect to LOGIN_URL."""

    PROTECTED = [
        ("user", {}),
        ("editprofile", {}),
        ("editratings", {}),
        ("captain", {}),
        ("junta", {}),
    ]

    def test_anonymous_redirected_to_login(self):
        for name, kwargs in self.PROTECTED:
            resp = self.client.get(reverse(name, kwargs=kwargs))
            self.assertEqual(
                resp.status_code, 302,
                "{} should redirect anonymous users, got {}".format(name, resp.status_code),
            )
            self.assertIn(
                settings.LOGIN_URL.split("/")[1], resp["Location"],
                "{} did not redirect to the login URL: {}".format(name, resp["Location"]),
            )


class AuthenticatedViewSmokeTest(TestCase):
    """Logged-in access to the user dashboard pages should not 500."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="smoke@example.com", password="pw", first_name="Smoke", last_name="Test"
        )

    def setUp(self):
        self.client.force_login(self.user)

    def assertNot5xx(self, name, **kwargs):
        resp = self.client.get(reverse(name, kwargs=kwargs))
        self.assertLess(
            resp.status_code, 500, "{} returned {}".format(name, resp.status_code)
        )

    def test_user_dashboard(self):
        self.assertNot5xx("user")

    def test_edit_profile(self):
        self.assertNot5xx("editprofile")

    def test_edit_ratings(self):
        self.assertNot5xx("editratings")
