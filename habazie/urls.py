from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^login$', 'django.contrib.auth.views.login',
                           {'template_name': 'login_page.html'}, name='login'),
                       url(r'^logout$', 'django.contrib.auth.views.logout_then_login', name='logout'),
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^accounts/', include('facebook.urls')),
                       url(r'^', include('hours.urls')),
)

urlpatterns += staticfiles_urlpatterns()
