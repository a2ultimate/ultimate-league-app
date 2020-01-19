from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^', include('ultimate.index.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^captain/', include('ultimate.captain.urls')),
    url(r'^junta/', include('ultimate.junta.urls')),
    url(r'^leagues/', include('ultimate.leagues.urls')),
    url(r'^user/', include('ultimate.user.urls')),

    url(r'^captcha/', include('captcha.urls')),
    url(r'^hijack/', include('hijack.urls')),
    ]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
