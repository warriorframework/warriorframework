from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.CoreView.as_view(), name='index'),
    url(r'^get_file_explorer_data/$', views.get_file_explorer_data, name='get_file_explorer_data'),
    url(r'^read_config_file/$', views.read_config_file, name='read_config_file'),
    url(r'^check_if_file_exists/$', views.check_if_file_exists, name='check_if_file_exists'),
    url(r'^refresh_landing_page/$', views.refresh_landing_page, name='refresh_landing_page'),
]
