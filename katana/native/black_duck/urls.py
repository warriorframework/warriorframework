from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^settings', views.settings, name='settings'),
    url(r'^create', views.create_project, name='create'),
    url(r'^gettree', views.get_tree, name="gettree"),
]
