from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.BrandNewAppView.as_view(), name='userapp'),
]
