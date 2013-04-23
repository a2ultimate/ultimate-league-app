from django.conf.urls.defaults import *

from ultimate.leagues.signals import *

urlpatterns = patterns('ultimate.leagues.views',
	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/$', 'index', {}, 'league_index'),
	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', 'summary', {}, 'league_summary'),
	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/details/$', 'details', {}, 'league_details'),
	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/players/$', 'players', {}, 'league_players'),
	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/teams/$', 'teams', {}, 'league_teams'),

	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/group/$', 'group', {}, 'league_group'),

	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/registration/$', 'registration', {}, 'league_registration'),
	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/registration/section/(?P<section>[^/]+)/$', 'registration', {}, 'league_registration_section'),

	(r'^payment/notification/callback/for/ultimate/league/', include('paypal.standard.ipn.urls')),
)
