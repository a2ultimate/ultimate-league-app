from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

urlpatterns = patterns('ultimate.index.views',
	(r'^$', 'index', {}, 'home'),
	(r'^update_feed/$', 'update_feed', {}, 'update_feed'),

	(r'^about/$', 'content', {'url': 'about_us/'}, 'about_us'),
	(r'^comments/$', 'content', {'url': 'comments/'}, 'comments'),
	(r'^contact/$', 'content', {'url': 'contacts/'}, 'contact'),
	(r'^pickup/$', 'content', {'url': 'pickup/'}, 'pickup'),
	(r'^rules/$', 'content', {'url': 'rules/'}, 'rules'),
	(r'^weather/$', 'content', {'url': 'weather/'}, 'weather'),
	(r'^welcome/$', 'content', {'url': 'welcome/'}, 'welcome'),
	(r'^youth/$', 'content', {'url': 'youth/'}, 'youth'),
)
