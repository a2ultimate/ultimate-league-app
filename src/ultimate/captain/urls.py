from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.index, {}, 'captain'),
    url(r'^team/(?P<team_id>[^/]+)/edit/$', views.editteam, {}, 'captaineditteam'),
    url(r'^team/(?P<team_id>[^/]+)/export/$', views.exportteam, {}, 'captain_team_export'),
    url(r'^team/(?P<team_id>[^/]+)/playersurvey/$', views.playersurvey, {}, 'playersurvey'),
    url(r'^team/(?P<team_id>[^/]+)/game/(?P<game_id>[^/]+)/gamereport/$', views.gamereport, {}, 'gamereport'),
    ]
