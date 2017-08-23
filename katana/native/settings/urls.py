from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^email_setting_handler', views.email_setting_handler, name='email_setting_handler'),
    url(r'^secret_handler', views.secret_handler, name='secret_handler'),
]
