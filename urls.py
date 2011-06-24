from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import provision.urls as provision

from django.http import HttpResponseRedirect as redirect
from django.contrib.auth.views import login, logout

admin.autodiscover()

urlpatterns = patterns('',
    # (r'^telepy/', include('telepy.foo.urls')),
    (r'^$', lambda x: redirect('/admin/')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    #(r'^admin/stat/', include(statistic)),
    (r'^provision/', include(provision)),
)
