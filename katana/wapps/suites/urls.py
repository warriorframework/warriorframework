from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'editSuite', views.editSuite, name='editSuite'),
    url(r'getSuiteDataBack', views.getSuiteDataBack, name='getSuiteDataBack'),
    url(r'getJSONSuiteData', views.getJSONSuiteData, name='getJSONSuiteData'),
    url(r'getSuiteListTree', views.getSuiteListTree, name='getSuiteListTree'),
]
