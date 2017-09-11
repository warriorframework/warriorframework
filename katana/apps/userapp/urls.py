from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.UserAppView.as_view(), name='userapp'),
]
