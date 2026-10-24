from django.conf import settings
from django.urls import include, re_path

from .signals import paypal_callback
from . import views

urlpatterns = [
    re_path(r'^(?P<year>\d{4})/$', views.index, {}, 'league_index_year'),
    re_path(r'^(?P<year>\d{4})/(?P<season>[^/]+)/$', views.index, {}, 'league_index_season'),

    re_path(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.summary, {}, 'league_summary'),
    re_path(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/details/$', views.details, {}, 'league_details'),
    re_path(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/players/$', views.players, {}, 'league_players'),
    re_path(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/teams/$', views.teams, {}, 'league_teams'),

    re_path(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/group/$', views.group, {}, 'league_group'),

    re_path(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/registration/$', views.registration, {}, 'league_registration'),
    re_path(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/registration/section/(?P<section>[^/]+)/$', views.registration, {}, 'league_registration_section'),
    re_path(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/registration-complete/$', views.registrationcomplete, {}, 'league_registration_complete'),

    re_path(r'^paypal/', include('paypal.standard.ipn.urls')),
    ]
