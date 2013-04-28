from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tree_model.api import RegionResource

region_resource = RegionResource()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TreeModel.views.home', name='home'),
    # url(r'^TreeModel/', include('TreeModel.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    (r'^api/', include(region_resource.urls)),

)
