from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new_app', views.new_app, name='new_app'),
    url(r'^build_new_app', views.build_new_app, name='build_new_app')
]
