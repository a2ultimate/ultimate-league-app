from datetime import timedelta

from django.conf import settings

from ultimate.utils.google_api import GoogleAppsApi


def get_events():
    calendar_id = getattr(settings, 'GOOGLE_APPS_CALENDAR_ID', False)
    events = None
    since = timedelta(weeks=0)
    until = timedelta(weeks=12)

    try:
        if calendar_id:
            api = GoogleAppsApi()
            events = api.get_calendar_events(calendar_id, since, until)
    except:
        events = None

    return events
