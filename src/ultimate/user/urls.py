from django.urls import include, re_path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    re_path(r'^$', views.index, {}, 'user'),

    re_path(r'^log-in/$', auth_views.LoginView.as_view(template_name='user/login.html'), name='auth_log_in'),
    re_path(r'^log-out/$', auth_views.LogoutView.as_view(template_name='user/logout.html'), name='auth_log_out'),

    re_path(r'^password/reset/$', auth_views.PasswordResetView.as_view(
        success_url='/user/password/reset/done/',
        template_name='user/registration/password_reset_form.html',
        email_template_name='user/registration/password_reset_email.html',
        subject_template_name='user/registration/password_reset_subject.txt',
    ), name='password_reset'),
    re_path(r'^password/reset/done/$', auth_views.PasswordResetDoneView.as_view(
        template_name='user/registration/password_reset_done.html',
    ), name='password_reset_done'),
    re_path(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[^/]+)/$', auth_views.PasswordResetConfirmView.as_view(
        success_url='/user/password/done/',
        template_name='user/registration/password_reset_confirm.html',
    ), name='password_reset_confirm'),
    re_path(r'^password/done/$', auth_views.PasswordResetCompleteView.as_view(
        template_name='user/registration/password_reset_complete.html',
    ), name='password_reset_complete'),

    re_path(r'^sign-up/$', views.signup, {}, 'registration_register'),

    re_path(r'^edit/profile/$', views.editprofile, {}, 'editprofile'),
    re_path(r'^edit/ratings/$', views.editratings, {}, 'editratings'),
    ]
