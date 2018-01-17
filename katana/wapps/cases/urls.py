from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.CasesView.as_view(), name='index'),
    url(r'^get_list_of_cases/$', views.get_list_of_cases, name='get_list_of_cases'),
    url(r'^get_file/$', views.get_file, name='get_file'),
]
