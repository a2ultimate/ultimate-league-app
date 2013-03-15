from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Uncomment the admin/doc line below and add 'django.contrib.admindocs'
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	(r'^', include('a2ultimate.index.urls')),
	(r'^admin/', include(admin.site.urls)),
	(r'^captain/', include('a2ultimate.captain.urls')),
	(r'^forum/', include('pybb.urls', namespace='pybb')),
	(r'^junta/', include('a2ultimate.junta.urls')),
	(r'^leagues/', include('a2ultimate.leagues.urls')),
	(r'^user/', include('a2ultimate.user.urls')),
)
