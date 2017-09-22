from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.WappStoreView.as_view(), name='wappstore'),
]
