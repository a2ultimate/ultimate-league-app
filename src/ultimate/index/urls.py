from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, {}, 'home'),
    re_path(r'^announcements/$', views.announcements, {}, 'announcements'),
    re_path(r'^news/(?P<url>[^/]+)$', views.news, {}, 'news_acticle'),

    re_path(r'^about/$', views.static, {'content_url': 'about'}, 'about'),
    re_path(r'^club/$', views.static, {'content_url': 'club'}, 'club'),
    re_path(r'^comments/$', views.static, {'content_url': 'comments'}, 'comments'),
    re_path(r'^contact/$', views.static, {'content_url': 'contacts'}, 'contact'),
    re_path(r'^pickup/$', views.static, {'content_url': 'pickup'}, 'pickup'),
    re_path(r'^rules/$', views.static, {'content_url': 'rules'}, 'rules'),
    re_path(r'^weather/$', views.static, {'content_url': 'weather'}, 'weather'),
    re_path(r'^welcome/$', views.static, {'content_url': 'welcome'}, 'welcome'),
    re_path(r'^youth/$', views.static, {'content_url': 'youth'}, 'youth'),

    re_path(r'^pages/(?P<content_url>[^/]+)/$', views.static, {}, 'static_page'),
    ]
