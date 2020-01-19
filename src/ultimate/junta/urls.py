from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.index, {}, 'junta'),

    url(r'^captainstatus/$', views.captainstatus, {}, 'captainstatus'),
    url(r'^captainstatus/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.captainstatus, {}, 'captainstatus_league'),

    url(r'^leagueresults/$', views.leagueresults, {}, 'leagueresults'),
    url(r'^leagueresults/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.leagueresults, {}, 'leagueresults_league'),

    url(r'^gamereports/$', views.gamereports, {}, 'gamereports'),
    url(r'^gamereports/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.gamereports, {}, 'gamereports_league'),
    url(r'^gamereports/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/(?P<game_id>[^/]+)/(?P<team_id>[^/]+)/$', views.gamereports, {}, 'gamereports_game'),

    url(r'^registrationexport/$', views.registrationexport, {}, 'registrationexport'),
    url(r'^registrationexport/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.registrationexport, {}, 'registrationexport_league'),

    url(r'^schedulegeneration/$', views.schedulegeneration, {}, 'schedulegeneration'),
    url(r'^schedulegeneration/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.schedulegeneration, {}, 'schedulegeneration_league'),

    url(r'^teamgeneration/$', views.teamgeneration, {}, 'teamgeneration'),
    url(r'^teamgeneration/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.teamgeneration, {}, 'teamgeneration_league'),
    ]
