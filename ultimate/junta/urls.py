from django.conf.urls.defaults import *

urlpatterns = patterns('ultimate.junta.views',
	(r'^$', 'index', {}, 'junta'),

	(r'^captainstatus/$', 'captainstatus', {}, 'captainstatus'),
	(r'^captainstatus/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', 'captainstatus', {}, 'captainstatus_league'),

	(r'^registrationexport/$', 'registrationexport', {}, 'registrationexport'),
	(r'^registrationexport/(?P<year>\d{4})/(?P<season>[^/]+)/(?P<division>[^/]+)/$', 'registrationexport', {}, 'registrationexport_league'),
)