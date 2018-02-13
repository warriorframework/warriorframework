from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
 	url(r'editCase', views.editCase , name='editCase'),
    url(r'getCaseDataBack', views.getCaseDataBack , name='getCaseDataBack'),
 	url(r'getListOfActions', views.getListOfActions , name='getListOfActions'),
 	url(r'getListOfKeywords', views.getListOfKeywords , name='getListOfKeywords'),
 	url(r'getListOfComments', views.getListOfComments , name='getListOfComments'),
 	url(r'getJSONcaseDataBack', views.getJSONcaseDataBack , name='getJSONcaseDataBack'),
	url(r'getCaseListTree', views.getCaseListTree , name='getCaseListTree'),


]
 	 	