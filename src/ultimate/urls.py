from django.conf import settings
from django.conf.urls import patterns, url, include


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('ultimate.index.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^captain/', include('ultimate.captain.urls')),
    (r'^junta/', include('ultimate.junta.urls')),
    (r'^leagues/', include('ultimate.leagues.urls')),
    (r'^user/', include('ultimate.user.urls')),

    (r'^forum/', include('pybb.urls', namespace='pybb')),

    (r'^captcha/', include('captcha.urls')),
    (r'^hijack/', include('hijack.urls')),
)

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
