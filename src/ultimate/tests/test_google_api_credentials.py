"""Tests for GoogleAppsApi credential construction.

The credential path in GoogleAppsApi.__init__ moved from the dead oauth2client
to google-auth during the Django upgrade. The existing google_api tests run
under test settings that blank GOOGLE_APPS_API_CREDENTIALS_FILE, so __init__
skips credential loading entirely and never exercises this code. These tests
fill that gap: with credentials configured, __init__ must build google-auth
service-account credentials, apply domain-wide delegation (with_subject), and
wrap them in an AuthorizedHttp -- without touching a real keyfile or network.
"""

from unittest import mock

from django.test import TestCase, override_settings

from ultimate.utils import google_api
from ultimate.utils.google_api import GoogleAppsApi


@override_settings(
    GOOGLE_APPS_API_CREDENTIALS_FILE="/tmp/fake-key.json",
    GOOGLE_APPS_API_SCOPES=("https://www.googleapis.com/auth/admin.directory.group",),
    GOOGLE_APPS_API_ACCOUNT="admin@example.com",
)
class CredentialConstructionTest(TestCase):
    def test_builds_authorized_http_with_delegation(self):
        fake_delegated = mock.Mock(name="delegated_credentials")
        fake_base = mock.Mock(name="base_credentials")
        fake_base.with_subject.return_value = fake_delegated

        with mock.patch.object(
            google_api.service_account.Credentials,
            "from_service_account_file",
            return_value=fake_base,
        ) as from_file, mock.patch.object(
            google_api, "google_auth_httplib2"
        ) as gah:
            api = GoogleAppsApi()

        # Credentials loaded from the configured keyfile with the configured scopes.
        from_file.assert_called_once()
        _, kwargs = from_file.call_args
        self.assertIn("admin.directory.group", kwargs["scopes"][0])

        # Domain-wide delegation impersonates the configured account.
        fake_base.with_subject.assert_called_once_with("admin@example.com")

        # The delegated credentials are wrapped in an AuthorizedHttp, which
        # becomes the http transport the API methods pass to build()/execute().
        gah.AuthorizedHttp.assert_called_once()
        args, _ = gah.AuthorizedHttp.call_args
        self.assertIs(args[0], fake_delegated)
        self.assertIs(api.http, gah.AuthorizedHttp.return_value)


class MissingCredentialsTest(TestCase):
    @override_settings(GOOGLE_APPS_API_CREDENTIALS_FILE="")
    def test_no_credentials_leaves_http_none(self):
        # This is the configuration the test suite runs under: with no keyfile,
        # __init__ must skip credential loading and leave http as None so the
        # object can still be constructed (the API surface is mocked in tests).
        api = GoogleAppsApi()
        self.assertIsNone(api.http)
