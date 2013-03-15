from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

urlpatterns = patterns('ultimate.user.views',
	(r'^$', 'index', {}, 'user'),

	(r'^login/$', login, {'template_name': 'user/login.html'}, 'auth_login'),
	(r'^logout/$', logout, {'template_name': 'user/logout.html'}, 'auth_logout'),
	(r'^$', 'index', {}, 'auth_password_change'),

	(r'^signup/$', 'signup', {}, 'registration_register'),
	(r'^editprofile/$', 'editprofile', {}, 'editprofile'),
	(r'^editskills/$', 'editskills', {}, 'editskills'),
)