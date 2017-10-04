from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.AssemblerView.as_view(), name='assembler'),
    url(r'^get_config_file/$', views.ConfigurationFileOps.as_view(), name='get_config_file'),
]
