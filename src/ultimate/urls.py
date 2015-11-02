from django.conf.urls import patterns, url, include
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Uncomment the admin/doc line below and add 'django.contrib.admindocs'
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	(r'^', include('ultimate.index.urls')),
	(r'^admin/', include(admin.site.urls)),
	(r'^captain/', include('ultimate.captain.urls')),
	(r'^forum/', include('pybb.urls', namespace='pybb')),
	(r'^junta/', include('ultimate.junta.urls')),
	(r'^leagues/', include('ultimate.leagues.urls')),
	(r'^user/', include('ultimate.user.urls')),
)
