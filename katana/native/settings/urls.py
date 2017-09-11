from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^email_setting_handler', views.email_setting_handler, name='email_setting_handler'),
    url(r'^secret_handler', views.secret_handler, name='secret_handler'),
    url(r'^jira_setting_handler', views.jira_setting_handler, name='jira_setting_handler'),
    url(r'^general_setting_handler', views.general_setting_handler, name='general_setting_handler'),
    url(r'^profile_setting_handler', views.profile_setting_handler, name='profile_setting_handler'),

]
