from django.conf.urls import patterns, url, include

urlpatterns = patterns('ultimate.junta.views',
	(r'^$', 'index', {}, 'junta'),

	(r'^captainstatus/$', 'captainstatus', {}, 'captainstatus'),
	(r'^captainstatus/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', 'captainstatus', {}, 'captainstatus_league'),

	(r'^leagueresults/$', 'leagueresults', {}, 'leagueresults'),
	(r'^leagueresults/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', 'leagueresults', {}, 'leagueresults_league'),

	(r'^gamereports/$', 'gamereports', {}, 'gamereports'),
	(r'^gamereports/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', 'gamereports', {}, 'gamereports_league'),
	(r'^gamereports/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/(?P<game_id>[^/]+)/(?P<team_id>[^/]+)/$', 'gamereports', {}, 'gamereports_game'),

	(r'^registrationexport/$', 'registrationexport', {}, 'registrationexport'),
	(r'^registrationexport/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', 'registrationexport', {}, 'registrationexport_league'),

	(r'^schedulegeneration/$', 'schedulegeneration', {}, 'schedulegeneration'),
	(r'^schedulegeneration/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', 'schedulegeneration', {}, 'schedulegeneration_league'),

	(r'^teamgeneration/$', 'teamgeneration', {}, 'teamgeneration'),
	(r'^teamgeneration/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', 'teamgeneration', {}, 'teamgeneration_league'),
)