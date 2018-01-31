from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.CasesView.as_view(), name='index'),
    url(r'^get_list_of_cases/$', views.get_list_of_cases, name='get_list_of_cases'),
    url(r'^get_file/$', views.get_file, name='get_file'),
    url(r'^get_details_template/$', views.get_details_template, name='get_details_template'),
    url(r'^get_reqs_template/$', views.get_reqs_template, name='get_reqs_template'),
    url(r'^get_steps_template/$', views.get_steps_template, name='get_steps_template'),
    url(r'^get_details_display_template/$', views.get_details_display_template, name='get_details_display_template'),
]
