from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.CoreView.as_view(), name='index'),
]