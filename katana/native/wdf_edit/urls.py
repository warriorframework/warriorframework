from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^json', views.get_json, name='json'),
    url(r'^post', views.on_post, name='post'),
    url(r'^tree', views.file_list, name="files"),
]
