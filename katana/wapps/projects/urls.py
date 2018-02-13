from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'editProject', views.editProject, name='editProject'),
    url(r'getProjectDataBack', views.getProjectDataBack, name='getProjectDataBack'),
    url(r'getJSONProjectData', views.getJSONProjectData, name='getJSONProjectData'),
 	url(r'getProjectListTree', views.getProjectListTree, name='getProjectListTree'),

    #url(r'^email_setting_handler', views.email_setting_handler, name='email_setting_handler'),
    #url(r'^secret_handler', views.secret_handler, name='secret_handler'),
    #url(r'^jira_setting_handler', views.jira_setting_handler, name='jira_setting_handler'),
]
