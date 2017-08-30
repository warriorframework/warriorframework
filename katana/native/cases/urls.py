from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
<<<<<<< HEAD
 	url(r'editCase', views.editCase , name='editCase'),
    
=======
    url(r'^email_setting_handler', views.email_setting_handler, name='email_setting_handler'),
    url(r'^secret_handler', views.secret_handler, name='secret_handler'),
    url(r'^jira_setting_handler', views.jira_setting_handler, name='jira_setting_handler'),
>>>>>>> 1589a90... Saving back of Projects and Suites in new UI
]
