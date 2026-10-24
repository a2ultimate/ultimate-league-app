from django.urls import include, re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, {}, 'junta'),

    re_path(r'^concussion-compliance/$', views.concussion_compliance, {}, 'concussion_compliance'),
    re_path(r'^concussion-compliance/(?P<player_user_id>[^/]+)/$', views.concussion_compliance, {}, 'concussion_compliance_user'),

    re_path(r'^captainstatus/$', views.captainstatus, {}, 'captainstatus'),
    re_path(r'^captainstatus/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.captainstatus, {}, 'captainstatus_league'),

    re_path(r'^leagueresults/$', views.leagueresults, {}, 'leagueresults'),
    re_path(r'^leagueresults/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.leagueresults, {}, 'leagueresults_league'),

    re_path(r'^gamereports/$', views.gamereports, {}, 'gamereports'),
    re_path(r'^gamereports/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.gamereports, {}, 'gamereports_league'),
    re_path(r'^gamereports/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/(?P<game_id>[^/]+)/(?P<team_id>[^/]+)/$', views.gamereports, {}, 'gamereports_game'),

    re_path(r'^registrationexport/$', views.registrationexport, {}, 'registrationexport'),
    re_path(r'^registrationexport/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.registrationexport, {}, 'registrationexport_league'),

    re_path(r'^schedulegeneration/$', views.schedulegeneration, {}, 'schedulegeneration'),
    re_path(r'^schedulegeneration/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.schedulegeneration, {}, 'schedulegeneration_league'),

    re_path(r'^teamgeneration/$', views.teamgeneration, {}, 'teamgeneration'),
    re_path(r'^teamgeneration/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', views.teamgeneration, {}, 'teamgeneration_league'),
    ]
