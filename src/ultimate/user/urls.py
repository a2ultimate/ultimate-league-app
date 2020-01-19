from django.conf.urls import patterns, url, include
from django.contrib.auth.views import login, logout, password_reset, password_reset_done, password_reset_confirm, password_reset_complete

from . import views

urlpatterns = [
    url(r'^$', views.index, {}, 'user'),

    url(r'^log-in/$', login, {'template_name': 'user/login.html'}, 'auth_log_in'),
    url(r'^log-out/$', logout, {'template_name': 'user/logout.html'}, 'auth_log_out'),

    url(r'^password/reset/$', password_reset, {'post_reset_redirect': '/user/password/reset/done/', 'template_name': 'user/registration/password_reset_form.html',
                                           'email_template_name': 'user/registration/password_reset_email.html', 'subject_template_name': 'user/registration/password_reset_subject.txt', }, 'password_reset'),
    url(r'^password/reset/done/$', password_reset_done,
       {'template_name': 'user/registration/password_reset_done.html'}, 'password_reset_done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', password_reset_confirm, {
       'post_reset_redirect': '/user/password/done/', 'template_name': 'user/registration/password_reset_confirm.html'}, 'password_reset_confirm'),
    url(r'^password/done/$', password_reset_complete,
       {'template_name': 'user/registration/password_reset_complete.html'}, 'password_reset_confirm'),

    url(r'^sign-up/$', views.signup, {}, 'registration_register'),

    url(r'^edit/profile/$', views.editprofile, {}, 'editprofile'),
    url(r'^edit/ratings/$', views.editratings, {}, 'editratings'),
    ]
