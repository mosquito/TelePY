from django.conf.urls.defaults import *
from django.contrib import admin
from provision.views import *
admin.autodiscover()

urlpatterns = patterns('',
    (r'(?P<alias>\S{1,100})/(?P<mac>\S{8,17})/(?P<sn>\S{1,100}).xml$', provision),
    (r'dev.voip.zone$', dns),
    (r'dhcpd.conf$', dhcp),
)
