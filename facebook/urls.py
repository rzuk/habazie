from django.conf.urls import patterns, url
from facebook.views import EmailPermissionsRedirect, AssociateCallback

urlpatterns = patterns('',
    url(r'^login/(?P<provider>(\w|-)+)/$', EmailPermissionsRedirect.as_view(), name='allaccess-login'),
    url(r'^callback/(?P<provider>(\w|-)+)/$', AssociateCallback.as_view(), name='allaccess-callback'),
)
