from django.conf.urls import url
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    url(r'^$', views.WappManagementView.as_view(), name='wapp_management'),
    url(r'^uninstall_an_app/$', views.uninstall_an_app, name='uninstall_an_app'),
    url(r'^install_an_app/$', views.install_an_app, name='install_an_app'),
    url(r'^create_config/$', views.AppInstallConfig.as_view(), name='create_config'),
    url(r'^load_configs/$', views.load_configs, name='load_configs'),
    url(r'^open_config/$', views.open_config, name='open_config'),
    url(r'^validate_app_path/$', views.validate_app_path, name='validate_app_path'),
    url(r'^update_installed_apps_section/$', views.update_installed_apps_section, name='update_installed_apps_section'),
]
