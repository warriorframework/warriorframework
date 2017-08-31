from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.NewAppView.as_view(), name='userapp'),
]
