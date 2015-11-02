from django.conf.urls import patterns, url, include

urlpatterns = patterns('ultimate.captain.views',
	(r'^$', 'index', {}, 'captain'),
	(r'^team/(?P<teamid>[^/]+)/edit/$', 'editteam', {}, 'captaineditteam'),
	(r'^team/(?P<teamid>[^/]+)/playersurvey/$', 'playersurvey', {}, 'playersurvey'),
	(r'^team/(?P<teamid>[^/]+)/game/(?P<gameid>[^/]+)/gamereport/$', 'gamereport', {}, 'gamereport'),

)