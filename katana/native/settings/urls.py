from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^general_settings', views.general_settings, name='general_settings'),
]
