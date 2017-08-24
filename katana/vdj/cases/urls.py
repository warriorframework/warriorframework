from django.conf.urls import url

from . import views

urlpatterns = [
            url(r'^$', views.index, name='index'),
            url(r'index*.html', views.index, name='index'),
            url(r'editProject', views.editProject, name='editProject'),
            url(r'editSuite', views.editSuite, name='editSuite'),
            url(r'editCase', views.editCase, name='editCase'),
            url(r'getXMLfile', views.getXMLfile, name='getXMLfile'),
            url(r'getJSONfile', views.getJSONfile, name='getJSONfile'),
            url(r'listAllCases', views.listAllCases, name='listAllCases'),
            url(r'listAllSuites', views.listAllSuites, name='listAllSuites'),
            url(r'listAllProjects', views.listAllProjects, name='listAllProjects'),
            url(r'getDocStringForDriver',views.getDocStringForDriver, name='getDocStringForDriver'),
            url(r'getProjectDataBack',views.getProjectDataBack, name='getProjectDataBack'),
            url(r'getSuiteDataBack',views.getSuiteDataBack, name='getSuiteDataBack'),
            url(r'getCaseDataBack',views.getCaseDataBack, name='getCaseDataBack')
            
            ]
