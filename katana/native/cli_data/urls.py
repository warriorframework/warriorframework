from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.CliDataView.as_view(), name='wappstore'),
]
