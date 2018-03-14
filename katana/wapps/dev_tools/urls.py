from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new_app', views.new_app, name='new_app'),
    url(r'^edit_app', views.edit_app, name='edit_app'),
    url(r'^get_urls', views.get_urls, name='get_urls'),
    url(r'^open_file', views.open_file, name='open_file'),
    url(r'^save_file', views.save_file, name='save_file'),
    url(r'^build_new_app', views.build_new_app, name='build_new_app')
]
