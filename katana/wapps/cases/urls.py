from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.CasesView.as_view(), name='index'),
]
