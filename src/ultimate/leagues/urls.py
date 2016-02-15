from django.conf import settings
from django.conf.urls import patterns, url, include

from ultimate.leagues.signals import *

payment_callback_regex = r'^registration/payment/notification/callback/for/a2ultimate/secret/'
if getattr(settings, 'PAYPAL_CALLBACK_SECRET', False):
	payment_callback_regex = r'^registration/payment/' + settings.PAYPAL_CALLBACK_SECRET

urlpatterns = patterns('ultimate.leagues.views',
	(r'^(?P<year>\d{4})/$', 'index', {}, 'league_index_year'),
	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/$', 'index', {}, 'league_index_season'),

	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', 'summary', {}, 'league_summary'),
	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/details/$', 'details', {}, 'league_details'),
	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/players/$', 'players', {}, 'league_players'),
	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/teams/$', 'teams', {}, 'league_teams'),

	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/group/$', 'group', {}, 'league_group'),

	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/registration/$', 'registration', {}, 'league_registration'),
	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/registration/section/(?P<section>[^/]+)/$', 'registration', {}, 'league_registration_section'),
	(r'^(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/registration-complete/$', 'registrationcomplete', {}, 'league_registration_complete'),

	(payment_callback_regex, include('paypal.standard.ipn.urls')),

)
