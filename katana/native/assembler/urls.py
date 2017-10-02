from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.AssemblerView.as_view(), name='assembler'),
]
