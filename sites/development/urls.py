from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    # For anything not caught by a more specific rule above, hand over to
    # CMS serving mechanism
    url(r'', include('apps.simple_cms.urls')),
)

