from django.conf.urls import patterns, url, include

urlpatterns = patterns('ultimate.index.views',
    (r'^$', 'index', {}, 'home'),
    (r'^announcements/$', 'announcements', {}, 'announcements'),

    (r'^about/$', 'content', {'url': 'about/'}, 'about'),
    (r'^comments/$', 'content', {'url': 'comments/'}, 'comments'),
    (r'^contact/$', 'content', {'url': 'contacts/'}, 'contact'),
    (r'^pickup/$', 'content', {'url': 'pickup/'}, 'pickup'),
    (r'^rules/$', 'content', {'url': 'rules/'}, 'rules'),
    (r'^weather/$', 'content', {'url': 'weather/'}, 'weather'),
    (r'^welcome/$', 'content', {'url': 'welcome/'}, 'welcome'),
    (r'^youth/$', 'content', {'url': 'youth/'}, 'youth'),
)
