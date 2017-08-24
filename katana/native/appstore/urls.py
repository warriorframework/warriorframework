from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.AppStoreView.as_view(), name='appstore'),
    url(r'^uninstall_an_app/$', views.uninstall_an_app, name='uninstall_an_app'),
    url(r'^install_an_app/$', views.install_an_app, name='install_an_app'),
]
