from django.conf.urls.defaults import *

urlpatterns = patterns('ultimate.junta.views',
	(r'^$', 'index', {}, 'junta'),
)