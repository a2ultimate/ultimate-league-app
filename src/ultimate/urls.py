from django.conf import settings
from django.urls import include, re_path
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    re_path(r'^', include('ultimate.index.urls')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^captain/', include('ultimate.captain.urls')),
    re_path(r'^junta/', include('ultimate.junta.urls')),
    re_path(r'^leagues/', include('ultimate.leagues.urls')),
    re_path(r'^user/', include('ultimate.user.urls')),

    re_path(r'^captcha/', include('captcha.urls')),
    re_path(r'^hijack/', include('hijack.urls')),
    ]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
