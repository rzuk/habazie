from django.conf.urls import patterns, url

urlpatterns = patterns('hours.views',
                       url(r'^$', 'my_account', name='index'),
                       url(r'^stuff$', 'stuff', name='stuff'),
                       url(r'^item/(\d*)$', 'item', name='item'),
                       url(r'^hours', 'stuff', name='hours'),
)