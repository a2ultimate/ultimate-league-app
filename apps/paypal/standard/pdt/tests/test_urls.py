from django.conf.urls import patterns, url, include

urlpatterns = patterns('paypal.standard.pdt.views',
    (r'^pdt/$', 'pdt'),
)
