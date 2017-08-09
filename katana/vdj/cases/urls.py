from django.conf.urls import url

from . import views

urlpatterns = [
            url(r'^$', views.index, name='index'),
            url(r'editProject', views.editProject, name='editProject'),
            url(r'editSuite', views.editSuite, name='editSuite'),
            url(r'editCase', views.editCase, name='editCase'),
            url(r'getXMLfile', views.getXMLfile, name='getXMLfile'),
            url(r'getJSONfile', views.getJSONfile, name='getJSONfile')
            ]
