from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.CliDataView.as_view(), name='wappstore'),
    url(r'^get_default_file/$', views.CliDataFileClass.as_view(), name='get_default_file'),
    url(r'^save_testdata_file/$', views.CliDataFileClass.as_view(), name='save_testdata_file'),
]
