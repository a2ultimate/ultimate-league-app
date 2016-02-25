from datetime import timedelta

from django.conf import settings

from ultimate.utils.google_api import GoogleAppsApi


def get_events():
    calendar_id = getattr(settings, 'GOOGLE_APPS_CALENDAR_ID', False)
    events = []
    since = timedelta(weeks=4)

    if calendar_id:
        api = GoogleAppsApi()

        events = api.get_calendar_events(calendar_id, since)

    return events
