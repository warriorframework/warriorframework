from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.file_list, name='index'),
    url(r'^index', views.index, name='index'),
    # url(r'^json', views.get_json, name='json'),
    url(r'^post', views.on_post, name='post'),
    url(r'^tree', views.file_list, name="files"),
    url(r'^gettree', views.get_jstree_dir, name='filejson')
]
