from django.conf import settings
from django.conf.urls import url, include

from .signals import paypal_callback
from . import views

urlpatterns = [
    url(r'^(?P<year>\d{4})/$', views.index, {}, 'league_index_year'),
    url(r'^(?P<year>\d{4})/(?P<season>[^/]+)/$', views.index, {}, 'league_index_season'),

    url(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.summary, {}, 'league_summary'),
    url(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/details/$', views.details, {}, 'league_details'),
    url(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/players/$', views.players, {}, 'league_players'),
    url(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/teams/$', views.teams, {}, 'league_teams'),

    url(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/group/$', views.group, {}, 'league_group'),

    url(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/registration/$', views.registration, {}, 'league_registration'),
    url(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/registration/section/(?P<section>[^/]+)/$', views.registration, {}, 'league_registration_section'),
    url(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/registration-complete/$', views.registrationcomplete, {}, 'league_registration_complete'),

    url(r'^paypal$', include('paypal.standard.ipn.urls')),
    ]
