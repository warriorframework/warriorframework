from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.AssemblerView.as_view(), name='assembler'),
    url(r'^get_config_file/$', views.ConfigurationFileOps.as_view(), name='get_config_file'),
    url(r'^check_repo_availability/$', views.check_repo_availability, name='check_repo_availability'),
    url(r'^check_ws_repo_availability/$', views.check_ws_repo_availability, name='check_ws_repo_availability'),
]
