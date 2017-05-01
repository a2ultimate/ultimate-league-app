from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, {}, 'home'),
    url(r'^announcements/$', views.announcements, {}, 'announcements'),

    url(r'^about/$', views.static, {'content_url': 'about'}, 'about'),
    url(r'^club/$', views.static, {'content_url': 'club'}, 'club'),
    url(r'^comments/$', views.static, {'content_url': 'comments'}, 'comments'),
    url(r'^contact/$', views.static, {'content_url': 'contacts'}, 'contact'),
    url(r'^pickup/$', views.static, {'content_url': 'pickup'}, 'pickup'),
    url(r'^rules/$', views.static, {'content_url': 'rules'}, 'rules'),
    url(r'^weather/$', views.static, {'content_url': 'weather'}, 'weather'),
    url(r'^welcome/$', views.static, {'content_url': 'welcome'}, 'welcome'),
    url(r'^youth/$', views.static, {'content_url': 'youth'}, 'youth'),

    url(r'^pages/(?P<content_url>[^/]+)/$', views.static),
]
