from django.conf.urls.defaults import *

urlpatterns = patterns('a2ultimate.junta.views',
	(r'^$', 'index', {}, 'junta'),
)