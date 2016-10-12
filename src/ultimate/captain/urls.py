from django.conf.urls import patterns, url, include

urlpatterns = patterns('ultimate.captain.views',
	(r'^$', 'index', {}, 'captain'),
	(r'^team/(?P<team_id>[^/]+)/edit/$', 'editteam', {}, 'captaineditteam'),
	(r'^team/(?P<team_id>[^/]+)/export/$', 'exportteam', {}, 'captain_team_export'),
	(r'^team/(?P<team_id>[^/]+)/playersurvey/$', 'playersurvey', {}, 'playersurvey'),
	(r'^team/(?P<team_id>[^/]+)/game/(?P<game_id>[^/]+)/gamereport/$', 'gamereport', {}, 'gamereport'),

)
