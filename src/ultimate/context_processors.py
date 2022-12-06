from django.conf import settings


def menu_leagues(request):
    from ultimate.leagues.models import League

    leagues = League.objects.filter(state__in=['cancelled', 'closed', 'open', 'preview']).reverse()
    leagues = [league for league in leagues if league.is_visible(request.user)]

    return {'menu_leagues': leagues}


def menu_items_nav(request):
    from ultimate.index.models import StaticMenuItems

    menu_items = StaticMenuItems.objects.filter(location='nav')

    return {'menu_items_nav': menu_items}


def menu_items_home_sidebar(request):
    from ultimate.index.models import StaticMenuItems

    menu_items = StaticMenuItems.objects.filter(location='home_sidebar')

    return {'menu_items_home_sidebar': menu_items}


def google_analytics(request):
    measurement_id = None

    if not settings.DEBUG:
        measurement_id = getattr(settings, 'GOOGLE_ANALYTICS_MEASUREMENT_ID', None)

    return {
        'GOOGLE_ANALYTICS_MEASUREMENT_ID': measurement_id,
    }


def social_links(request):
    return {
        'SOCIAL_LINKS': getattr(settings, 'SOCIAL', []),
    }
