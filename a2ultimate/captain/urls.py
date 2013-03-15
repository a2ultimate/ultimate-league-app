from django.conf.urls.defaults import *

urlpatterns = patterns('a2ultimate.captain.views',
	(r'^$', 'index', {}, 'captain'),
	(r'^team/(?P<teamid>[^/]+)/edit/$', 'editteam', {}, 'captaineditteam'),
	(r'^team/(?P<teamid>[^/]+)/playersurvey/$', 'playersurvey', {}, 'playersurvey'),
	(r'^team/(?P<teamid>[^/]+)/game/(?P<gameid>[^/]+)/gamereport/$', 'gamereport', {}, 'gamereport'),

)