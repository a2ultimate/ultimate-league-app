from django.urls import include, re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, {}, 'captain'),
    re_path(r'^team/(?P<team_id>[^/]+)/edit/$', views.editteam, {}, 'captaineditteam'),
    re_path(r'^team/(?P<team_id>[^/]+)/export/$', views.exportteam, {}, 'captain_team_export'),
    re_path(r'^team/(?P<team_id>[^/]+)/playersurvey/$', views.playersurvey, {}, 'playersurvey'),
    re_path(r'^team/(?P<team_id>[^/]+)/game/(?P<game_id>[^/]+)/gamereport/$', views.gamereport, {}, 'gamereport'),
    ]
